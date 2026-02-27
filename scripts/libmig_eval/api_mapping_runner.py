import sys

import pandas as pd
from libmig.api_mapping.api_mapper import APIMapper
from libmig.lib_index.lib_index import LibIndex
from libmig.utils.venv import get_venv, Venv
from random import shuffle

from libmig_eval.mig_runner import paths
from libmig_eval.util.lib_db import LibPairDb
from libmig_eval.util.models import LibPair


def run_api_mapping():
    venv = get_venv(paths.project_group_root / "lib_index_venv")
    if not venv.exists():
        venv.create()

    lp_db = LibPairDb()
    runer = APIMappingRunner(venv, lp_db)
    runer.run()


class APIMappingRunner:
    def __init__(self, venv: Venv, lp_db: LibPairDb):
        self.venv = venv
        self.lp_db = lp_db

        excluded_libs = {
            "pygraphviz",  # pip install fails: Could not build wheels
            "cchardet",  # pip install fails: Could not build wheels
            "cupy",  # pip install fails: Could not build wheels
            "tensorflow",  # no top-level import names found
        }

        # shuffling is done so that when run multiple times, the order of processing is different.
        # this allows running multiple instances in parallel, speeding up the process
        self.included_libs = list((self.lp_db.source_libs() | self.lp_db.target_libs()) - excluded_libs)
        self.included_libs = ["requests"]
        shuffle(self.included_libs)
        self.included_pairs = [pair for pair in self.lp_db.all_analogous() if
                               pair.source in self.included_libs and pair.target in self.included_libs]
        shuffle(self.included_pairs)

    def run(self):
        # self.install_libs()
        # self.index_libs()
        self.summarize_docs()
        self.summarize_mappings()

    def summarize_docs(self):
        libs = self.included_libs

        print(f"== summarizing {len(libs)} lib docs ==")
        rows = []
        api_count = []
        for i, lib in enumerate(libs, start=1):
            print(f"summarizing {lib}. {i}/{len(libs)}")
            lib_index = LibIndex.from_venv(lib, self.venv)
            apis = lib_index.get_public_apis()
            api_count.append((lib, len(apis)))
            print(f"  summarized {len(apis)} APIs from {lib}=={lib_index.module_version}")
            for api in apis:
                rows.append({
                    "lib": lib,
                    "version": lib_index.module_version,
                    "api": api.qualified_name,
                    "doc": api.doc,
                    "len": len(api.doc)
                })

        pd.DataFrame(rows).to_csv(paths.project_group_root / "lib_docs.csv", index=False)
        pd.DataFrame(api_count, columns=["lib", "api_count"]).to_csv(paths.project_group_root / "lib_api_count.csv",
                                                                     index=False)

    def install_libs(self):
        print(f"== installing {len(self.included_libs)} libraries ==")
        for i, lib in enumerate(self.included_libs, start=1):
            print(f"installing {lib}. {i}/{len(self.included_libs)}")
            self.venv.install(lib, "latest")

    def index_libs(self):
        libs = self.included_libs
        print(f"== indexing {len(libs)} libraries ==")
        for i, lib in enumerate(libs, start=1):
            print(f"indexing {lib}: {i}/{len(libs)}")
            try:
                lib_index = LibIndex.from_venv(lib, self.venv)
                apis = lib_index.get_all_apis()
                print(f"  indexed {len(apis)} APIs from {lib}=={lib_index.module_version}")
            except Exception as e:
                print(f"  failed to index {lib}")
                print(e)

    def summarize_mappings(self):
        rows = []
        analogous = self.included_pairs
        for i, pair in enumerate(analogous, start=1):
            print(f"Mapping {pair} {i}/{len(analogous)}")
            try:
                rows += list(self.build_mapping_for_one_pair(pair))
            except Exception as e:
                print(f"  failed to map {pair}. {e}", file=sys.stderr)

        pd.DataFrame(rows).to_csv(paths.project_group_root / "api_mapping.csv", index=False)
        print(f"Saved {len(rows)} mappings to {paths.project_group_root / 'api_mapping.csv'}")

    def build_mapping_for_one_pair(self, pair: LibPair):
        source_index = LibIndex.from_venv(pair.source, self.venv)
        target_index = LibIndex.from_venv(pair.target, self.venv)
        api_mapper = APIMapper(source_index, target_index)
        for source_api in source_index.get_public_apis():
            for target_api, sim in api_mapper.map(source_api):
                yield {
                    "source": pair.source,
                    "target": pair.target,
                    "source_api": source_api.qualified_name,
                    "target_api": target_api.qualified_name,
                    "similarity": sim,
                    "source_signature": source_api.signature,
                    "target_signature": target_api.signature,
                    "source_doc": source_api.doc,
                    "target_doc": target_api.doc
                }


if __name__ == '__main__':
    run_api_mapping()
