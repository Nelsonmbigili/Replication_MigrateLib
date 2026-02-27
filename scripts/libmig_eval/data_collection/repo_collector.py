import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from time import sleep

import pandas as pd
import requests

from libmig_eval.secrets import SECRETS
from libmig_eval.util import delete_dir
from libmig_eval.util.meta_db import MetaDb
from libmig_eval.util.models import encode_repo_id
from libmig_eval.util.paths import Paths
from libmig_eval.util.req_utils import read_requirements_file_from_github
from libmig_eval.util.run_cmd import run_cmd, run_with_venv, CommandError, pip_install, shallow_clone

QUEUED = "queued"
IN_PROGRESS = "in_progress"

paths = Paths()


class RepoFilter(ABC):
    @abstractmethod
    def should_exclude(self, meta: dict) -> (bool, str):
        """
        :param meta:
        :return: (bool, str) where the bool indicates whether the repo should be excluded and
        the str is the filtering category. The category is used to move the repo to the appropriate folder.
        """
        pass


class EmptyRepoFilter(RepoFilter):
    def should_exclude(self, meta: dict):
        return meta["loc"] == 0, "excluded.empty"


class LargeRepoFilter(RepoFilter):
    def __init__(self, max_size_kb: int):
        self.max_size_kb = max_size_kb

    def should_exclude(self, meta: dict):
        return meta["size_kb"] > self.max_size_kb, f"excluded.large/{self.max_size_kb}KB"


class NoRequirementsFileFilter(RepoFilter):
    def should_exclude(self, meta: dict):
        import requests
        requirements_url = f"https://raw.githubusercontent.com/{meta['name']}/{meta['commit']}/requirements.txt"
        response = requests.head(requirements_url)
        return response.status_code != 200, "excluded.no_requirements_file"


class NoTestFileByAPIFilter(RepoFilter):
    def should_exclude(self, meta: dict):
        api_key = SECRETS.github_access_token
        api_url = f"https://api.github.com/search/code"
        response = requests.get(api_url, params={
            "per_page": 1,
            "q": f"test in:path repo:{meta['name']}",
        }, headers={
            "Authorization": f"Bearer {api_key}",
            "X-GitHub-Api-Version": "2022-11-28"
        })
        r_json = response.json()

        if "message" in r_json and "rate limit" in r_json["message"]:
            print("GitHub Rate limit hit. Waiting for 30 seconds.")
            sleep(30)
            return self.should_exclude(meta)

        return r_json["total_count"] == 0, "excluded.no_test_file_by_api"


class NoDependenciesFilter(RepoFilter):
    def __init__(self, libs: set[str], exclusion_category: str):
        self.libs = libs
        self.exclusion_category = exclusion_category

    def should_exclude(self, meta: dict):
        requirements = read_requirements_file_from_github(meta['name'], meta['commit'])
        return not any(req.key in self.libs for req in requirements), self.exclusion_category


class UTestNotRunFilter(RepoFilter):
    def should_exclude(self, meta: dict):
        path = paths.repo_path(meta["id"])
        cov_path = path / "cov-report.json"
        utest_path = path / "test-report.json"
        if cov_path.exists() and utest_path.exists():
            summary = json.load((path / "test-report.json").open())["summary"]
            if summary["total"] > 0:
                return False, "excluded.test_not_run"
        return True, "excluded.test_not_run"


class LowPassingFilter(RepoFilter):
    def __init__(self, min_passing: float):
        self.min_passing = min_passing

    def should_exclude(self, meta: dict):
        path = paths.repo_path(meta["id"])
        summary = json.load((path / "test-report.json").open())["summary"]
        total_tests = summary["total"]
        pass_part = summary.get("passed", 0) / total_tests
        return pass_part < self.min_passing, f"excluded.low_passing/{int(pass_part * 100)}"


class LowCoverageFilter(RepoFilter):
    def __init__(self, min_coverage: float):
        self.min_coverage = min_coverage

    def should_exclude(self, meta: dict):
        path = paths.repo_path(meta["id"])
        cov = json.load((path / "cov-report.json").open())["totals"]
        percent_covered = cov["percent_covered"]
        return percent_covered < self.min_coverage * 100, f"excluded.low_coverage/{cov['percent_covered_display']}"


class RepoCollector:
    def __init__(self, meta_db: MetaDb, pre_test_filters: list[RepoFilter] = None,
                 post_test_filters: list[RepoFilter] = None):
        self.pre_test_filters = pre_test_filters or []
        self.post_test_filters = post_test_filters or []
        self._meta_db = meta_db
        self._clone_root = Path.cwd().parent / "repos"
        self._manual_excluded = set(pd.read_csv(meta_db.db_root / "manual_exclusion.csv")["repo"])

    def _try_exclude(self, meta, filters):
        repo_id = meta["id"]
        for filter in filters:
            should_exclude, category = filter.should_exclude(meta)
            if should_exclude:
                print(f"  {repo_id} is excluded by filter: {category}")
                self._meta_db.move(IN_PROGRESS, category, repo_id)
                return True
            print(f"  {repo_id} passes filter: {category}")

        return False

    def filter_one_repo(self, repo_id: str):
        success, meta = self._try_mark_in_progress(repo_id)
        if not success:
            print(f"  Meta file {repo_id} is not in queue. Perhaps another process moved it.")
            return

        if repo_id in self._manual_excluded:
            print(f"  {repo_id} is excluded manually.")
            self._meta_db.move(IN_PROGRESS, "excluded.manual", repo_id)
            return

        if self._try_exclude(meta, self.pre_test_filters):
            return

        if not self.post_test_filters:
            self._meta_db.move(IN_PROGRESS, "included", repo_id)
            return

        project_path = paths.repo_path(repo_id)
        try:
            print(f"  Cloning {repo_id}")
            shallow_clone(meta["name"], meta["commit"], project_path)
            print(f"  {repo_id} cloned.")
            print(f"  Creating virtual environment.")
            venv_path = self._create_venv(project_path)
            print(f"  Virtual environment created.")

            print(f"  Install dependencies.")
            pip_install(venv_path, "-r", project_path / "requirements.txt")
            pip_install(venv_path, "-e", project_path)
            pip_install(venv_path, "pytest", "pytest-cov", "pytest-json-report")
            print(f"  Dependencies installed.")

            print(f"  Running tests.")
            run_with_venv(venv_path, ["pytest", "-q", "--cov", "--cov-report=json:cov-report.json", "--json-report",
                                      "--json-report-file=test-report.json"],
                          cwd=project_path, raise_error=False, timeout_minutes=10)
            print(f"  Tests run.")

            if self._try_exclude(meta, self.post_test_filters):
                return

            meta["test_summary"] = json.load((project_path / "test-report.json").open())["summary"]
            meta["cov_summary"] = json.load((project_path / "cov-report.json").open())["totals"]
            self._meta_db.save(IN_PROGRESS, meta)

            self._meta_db.move(IN_PROGRESS, "included", repo_id)

            print(f"  -- Repo {repo_id} is included. --")
        except CommandError as e:
            print(f"  Command error: {e}")
            self._meta_db.move(IN_PROGRESS, f"excluded.command_error/{e.returncode}", repo_id)
        except TimeoutError as e:
            print(f"  Timeout: {e}")
            self._meta_db.move(IN_PROGRESS, "excluded.timeout", repo_id)
        except Exception as e:
            print(f"  Error: {e}")
            self._meta_db.move(IN_PROGRESS, "excluded.unhandled_error", repo_id)
        finally:
            delete_dir(project_path)

    def start_filtering(self):
        while meta := self._meta_db.load_next(QUEUED):
            print(f"Filtering {meta['id']} at {datetime.now().isoformat()} ")
            try:
                self.filter_one_repo(meta["id"])
            except Exception as e:
                print(f"Failed to process. Error: {e}")
            print()

    def _create_venv(self, project_path: Path):
        venv_path = project_path / ".venv"
        if not venv_path.exists():
            run_cmd(["python", "-m", "venv", venv_path])
        return venv_path

    def _try_mark_in_progress(self, repo_id):
        self._meta_db.move(QUEUED, IN_PROGRESS, repo_id)
        meta = self._meta_db.load(IN_PROGRESS, repo_id)
        return True, meta

    def load_meta_db(self, file: Path, load_in_category: str):
        import pandas as pd
        ghs_meta_list = pd.read_csv(file).to_dict(orient="records")
        total = len(ghs_meta_list)

        for i, ghs_meta in enumerate(ghs_meta_list, start=1):
            r_name = ghs_meta["name"].lower()
            commit = ghs_meta["lastCommitSHA"]
            id = encode_repo_id(r_name, commit)
            file_name = id + ".yaml"

            if any(f for f in self._meta_db.db_root.rglob(file_name) if f.is_file()):
                print(f"{i}/{total} {r_name}. Already exists. Skipping.")
                continue

            print(f"{i}/{total} {r_name}. Saving metadata.")

            repo = {
                "id": id,
                "name": r_name,
                "commit": commit,
                "default_branch": ghs_meta["defaultBranch"],
                "stars": ghs_meta["stargazers"],
                "size_kb": ghs_meta["size"],
                "created_at": ghs_meta["createdAt"],
                "last_commit_at": ghs_meta["lastCommit"],
                "loc": ghs_meta["codeLines"],
            }
            self._meta_db.save(load_in_category, repo)


def main():
    db_root = paths.repo_db_root
    meta_db = MetaDb(db_root)

    collector = RepoCollector(
        meta_db=meta_db,
        pre_test_filters=[
            EmptyRepoFilter(),
            LargeRepoFilter(10 * 1000),
            NoRequirementsFileFilter(),
            NoTestFileByAPIFilter(),
        ],
        post_test_filters=[
            UTestNotRunFilter(),
            LowPassingFilter(0.9),
            LowCoverageFilter(0.8),
        ],
    )
    # collector.load_meta_db(paths.seart_meta_list, QUEUED)
    collector.start_filtering()


#    meta_db.export_csv()


if __name__ == '__main__':
    main()
