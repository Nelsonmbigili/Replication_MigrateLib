import json
from collections import defaultdict
from time import sleep

import pandas as pd
import requests
from libmig.utils.cache import read_cache, write_cache
from libmig.utils.template import Template
from sentence_transformers import SentenceTransformer, util

from libmig_eval.secrets import SECRETS
from libmig_eval.util.meta_db import MetaDb
from libmig_eval.util.paths import Paths
from libmig_eval.util.req_utils import read_requirements_file_from_github

template = Template("""
Identify alternative Python libraries that offer similar functionality as "<lib_name>", 
allowing for potential replacement in applications.
The alternative libraries should be available on PyPI. 
Produce the result as a JSON list, having only the library names.
The produced library names should match the PyPI package names.    
""".strip())


class LibCollector:
    def __init__(self, lib_db: MetaDb, repo_db: MetaDb):
        self.lib_db = lib_db
        self.repo_db = repo_db
        self.libio_api_key = SECRETS.libio_api_key

    def collect(self):
        self.lib_db.db_root.mkdir(parents=True, exist_ok=True)
        src_libs = self.load_source_libs()

        for lib in sorted(src_libs.keys()):
            self.process_one_lib(lib, src_libs[lib])

        print("Exporting library list")
        self.lib_db.export_category_stats()

        print("Exporting library pairs")
        self.export_lib_pairs()

    def export_libs(self):
        libs = self.lib_db.all_ids("included")
        print(f"  Found {len(libs)} libraries")
        data = []
        for lib in libs:
            meta = self.lib_db.load("included", lib)
            data.append([meta["id"], meta["frequency"], meta["libio_info"]["dependents_count"],
                         len(meta["candidate_pairs"]), ";".join(meta["candidate_pairs"].keys())])

        df = pd.DataFrame(data, columns=["id", "frequency", "dependents_count", "num_candidates", "candidates"])
        df.to_csv(self.lib_db.db_root / "included_libs.csv", index=False)

    def export_lib_pairs(self):
        src_libs = self.lib_db.all_ids("included")
        all_targets = set()
        canidate_pairs = []
        for i, src in enumerate(src_libs, start=1):
            print(f"exporting lib pair {i}/{len(src_libs)} source libs")
            meta = self.lib_db.load("included", src)
            for candidate, similarity in meta["candidate_pairs"].items():
                candidate_info = self.get_libio_project(candidate)
                all_targets.add(candidate)
                canidate_pairs.append({
                    "pair_id": f"{src}__{candidate}",
                    "source": src,
                    "target": candidate,
                    "frequency": meta["frequency"],
                    "source_description": meta["libio_info"]["description"],
                    "target_description": candidate_info["description"],
                    "similarity": similarity,
                    "target_last_release": candidate_info["latest_release_published_at"].split("T")[0],
                    "source_url": f"https://pypi.org/project/{src}",
                    "target_url": f"https://pypi.org/project/{candidate}"
                })

        print(f"  Found {len(src_libs)} source libs, {len(all_targets)} target libs, {len(canidate_pairs)} pairs")
        pd.DataFrame(canidate_pairs).to_csv(self.lib_db.db_root / "candidate_lib_pairs.csv", index=False)

    def load_source_libs(self):
        list_path = self.lib_db.db_root / "source_libs.csv"
        if list_path.exists():
            print(f"Loading source libraries from cache. Remove {list_path} to refresh.")
            return pd.read_csv(list_path).set_index("lib")["frequency"].to_dict()

        repo_ids = self.repo_db.all_ids("included")
        print(f"Found {len(repo_ids)} repos")
        src_libs = defaultdict(int)
        for repo_id in repo_ids:
            print(f"Collecting from {repo_id}")
            repo_meta = self.repo_db.load("included", repo_id)
            requirements = read_requirements_file_from_github(repo_meta["name"], repo_meta["commit"])
            for req in requirements:
                src_libs[req.key] += 1

        print(f"Found {len(src_libs)} source libraries")
        pd.DataFrame(src_libs.items(), columns=["lib", "frequency"]).to_csv(list_path, index=False)
        return src_libs

    def process_one_lib(self, lib_name: str, frequency: int):

        if self.lib_db.find_meta_file(lib_name):
            print(f"Already processed {lib_name}")
            return

        print(f"Processing {lib_name}")

        meta = {"id": lib_name, "frequency": frequency}

        this_project = self.get_libio_project(lib_name)

        if not this_project:
            self.lib_db.save("excluded.not_on_libio", meta)
            print(f"Excluded {lib_name} because it is not on libio")
            return

        dependents_count = this_project["dependents_count"]
        meta["libio_info"] = this_project
        if dependents_count < 100:
            self.lib_db.save(f"excluded.too_few_dependents/{dependents_count}", meta)
            print(f"Excluded {lib_name} because it has too few dependents ({dependents_count})")
            return

        if not this_project["description"]:
            self.lib_db.save("excluded.no_description", meta)
            print(f"Excluded {lib_name} because the library has no description")
            return

        analogous_libs = request_llm(lib_name)
        analogous_libs = [lib.lower() for lib in analogous_libs]
        analogous_similarities = {}
        model = SentenceTransformer('all-MiniLM-L6-v2')
        this_vector = model.encode(this_project["description"])

        for that_lib_name in analogous_libs:
            that_project = self.get_libio_project(that_lib_name)
            if not that_project:
                continue
            if not that_project["description"]:
                continue
            that_vector = model.encode(that_project["description"])
            similarity = util.pytorch_cos_sim(this_vector, that_vector).item()
            analogous_similarities[that_lib_name] = similarity

        meta["candidate_pairs"] = analogous_similarities
        self.lib_db.save("included", meta)
        print(f"Processed {lib_name}. included.")

    def get_libio_project(self, lib_name: str):
        cache_file = f"libio/{lib_name}.json"
        content = read_cache(cache_file)
        if content:
            return json.loads(content)

        project_url = f"https://libraries.io/api/pypi/{lib_name}?api_key={self.libio_api_key}"
        project_response = requests.get(project_url)
        status_code = project_response.status_code
        if status_code == 429:
            print("LibIO rate limit hit. Waiting for 30 seconds")
            sleep(30)
            return self.get_libio_project(lib_name)

        if status_code == 404:
            return None
        elif status_code != 200:
            raise ValueError(f"Failed to get project info for {lib_name}. Status code: {status_code}")
        else:
            project = project_response.json()
            project.pop("versions", None)
            write_cache(cache_file, json.dumps(project, indent=2))
            return project


def request_llm(lib_name: str) -> list[str]:
    from openai import OpenAI
    api_key = SECRETS.openai_api_key
    client = OpenAI(api_key=api_key)

    prompt = template.render({"lib_name": lib_name})

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        response_format={
            "type": "json_object"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    result = json.loads(response.choices[0].message.content)

    # find the first response that is a list
    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, list):
                return value

    raise ValueError("No list found in response")


def main():
    paths = Paths()
    lib_db = MetaDb(paths.lib_db_root)
    repo_db = MetaDb(paths.repo_db_root)
    collector = LibCollector(lib_db, repo_db)
    collector.collect()


if __name__ == '__main__':
    main()
