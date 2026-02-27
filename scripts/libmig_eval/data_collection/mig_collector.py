from libmig.mig.libmig_runner import LibMigRunner

from libmig_eval.config import MODEL_NAME
from libmig_eval.util import delete_dir, create_project
from libmig_eval.util.lib_db import LibPairDb
from libmig_eval.util.meta_db import MetaDb
from libmig_eval.util.mig_utils import prepare_mig_repo, cleanup_mig_repo
from libmig_eval.util.models import Mig
from libmig_eval.util.paths import Paths
from libmig_eval.util.req_utils import read_requirements_file_from_github

paths = Paths()


class MigCollector:
    def __init__(self, repo_db: MetaDb, lib_pair_db: LibPairDb, mig_db: MetaDb, clean_repo_after_run):
        self.repo_db = repo_db
        self.lib_pair_db = lib_pair_db
        self.mig_db = mig_db
        self.clean_repo_after_run = clean_repo_after_run

    def collect(self):
        repo_ids = self.repo_db.all_ids("included")
        for repo_id in repo_ids:
            for mig in self.collect_from_repo(repo_id):
                self.mig_db.save("queued", mig)

        print(f"Collected {self.mig_db.count_all()} migs")

    def collect_from_repo(self, repo_id: str):
        repo = self.repo_db.load("included", repo_id)
        repo_name = repo["name"]
        commit = repo["commit"]
        requirements = read_requirements_file_from_github(repo_name, commit)
        migs = []
        for req in requirements:
            pairs = self.lib_pair_db.pairs_with_source(req.key)
            for pair in pairs:
                migs.append({
                    "id": f"{repo_id}__{pair.id}",
                    "repo": repo_name,
                    "commit": commit,
                    "source": pair.source,
                    "target": pair.target
                })

        print(f"{len(migs)} migs collecting from {repo_id}")
        return migs

    def filter(self):
        while mig := self.mig_db.load_next("queued"):
            mig = Mig(**mig)
            if not self.mig_db.move("queued", "in_progress", mig.id):
                continue
            try:
                self.filter_next(mig)
            except:
                self.mig_db.move("in_progress", "excluded.misc-error", mig.id)
            finally:
                if self.clean_repo_after_run:
                    cleanup_mig_repo(mig)

    def filter_next(self, mig: Mig):
        print(f"\n\nFiltering {mig.id}")
        prepare_mig_repo(mig)

        project = create_project(mig, rounds={"premig"})

        wf = LibMigRunner(project)
        wf.run()

        report = project.get_report()
        prep_report = report.get_premig_report()
        if prep_report.is_finished():
            cat = "included"
        else:
            cat = f"excluded.{prep_report.error_type.replace(' ', '_')}"

        print(f"  Moving {mig.id} to {cat}")
        self.mig_db.move("in_progress", cat, mig.id)


def cleanup_non_included_mig_results():
    mig_db = MetaDb(paths.mig_db_root)
    for cat in mig_db.all_categories():
        if cat == "included":
            continue
        mig_ids = mig_db.all_ids(cat)
        print(f"Cleaning up {cat}. {len(mig_ids)} migs")

        for mig_id in mig_ids:
            out_dir = paths.mig_out_path(mig_id)
            delete_dir(out_dir)


def main():
    repo_db = MetaDb(paths.repo_db_root)
    lib_db = LibPairDb()
    mig_db = MetaDb(paths.mig_db_root)

    collector = MigCollector(repo_db, lib_db, mig_db, False)
    collector.collect()
    #collector.filter()
    mig_db.export_category_stats()


if __name__ == '__main__':
    main()
