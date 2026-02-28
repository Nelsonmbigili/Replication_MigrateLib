from libmig.mig.libmig_runner import LibMigRunner
from libmig.mig.mig_report_models import encode_mig_id

from libmig_eval.mig_filter import *
from libmig_eval.util import create_project
from libmig_eval.util.meta_db import MetaDb
from libmig_eval.util.mig_db import MigDb
from libmig_eval.util.mig_utils import cleanup_mig_repo
from libmig_eval.util.models import Mig, decode_mig_id
from libmig_eval.util.paths import Paths

paths = Paths()


def migs_from_ids(mig_ids_str: str):
    mig_ids = [mid.strip() for mid in mig_ids_str.strip().splitlines(keepends=False)]

    def mig_from_id(mig_id):
        props = decode_mig_id(mig_id)
        mig_id = encode_mig_id(*props)
        return Mig(mig_id, *props)

    migs = [mig_from_id(mig_id) for mig_id in mig_ids if mig_id[0] != "-"]
    return migs


class MigRunner:
    def __init__(self, queue: MetaDb, rounds: set[str], dry_run: bool, use_cache: bool = True,
                 smart_skip_tests: bool = False, remove_repo_after_done=True):
        self.queue = queue
        self.rounds = rounds
        self.dry_run = dry_run
        self.use_cache = use_cache
        self.smart_skip_tests = smart_skip_tests
        self.remove_repo_after_done = remove_repo_after_done

    def run_all(self):
        print()
        print()

        while mig_meta := self.queue.load_next("queued"):
            mig = Mig(**mig_meta)
            print(f"Processing {mig.id}")
            try:
                self.run_one(mig)
            except Exception as e:
                # print the trace
                import traceback
                traceback.print_exception(e)
                self.queue.move("running", "error", mig.id)
                continue
            finally:
                if self.remove_repo_after_done:
                    cleanup_mig_repo(mig)

            print(f"Done {mig.id}")
            print(f"Repo path: {paths.mig_repo_path(mig)}")
            print(f"Venv path: {paths.mig_venv_path(mig)}")
            print(f"Report path: {paths.mig_out_path(mig)}")
            print(f"Open in pycharm: pycharm {paths.mig_repo_path(mig)}")
            print(f"Open is vscode: code {paths.mig_repo_path(mig)}")
            print()

        # MigSummarizer(migs).summarize(migs)
        print("Done")

    def run_one(self, mig: Mig):
        if not self.queue.move("queued", "running", mig.id):
            print(f"Skipping {mig.id} as it is already running or done.")
            return

        print(f"\nMigrating {mig.id}")

        project = create_project(mig, rounds=self.rounds, dry_run=self.dry_run,
                                 use_cache=self.use_cache, smart_skip_tests=self.smart_skip_tests)
        runner = LibMigRunner(project)
        runner.run()

        self.queue.move("running", "done", mig.id)


def mask_file_paths():
    import sys
    import traceback

    def mask_path(tb_str: str) -> str:
        # Replace any path starting with the prefix
        return tb_str.replace(paths.repos_root, '')

    def custom_excepthook(exc_type, exc_value, exc_tb):
        tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        masked_tb = mask_path(tb)
        print(masked_tb, file=sys.stderr)

    # Set global exception handler
    sys.excepthook = custom_excepthook


def main():
    mask_file_paths()
    # process_que_db = MetaDb(paths.project_group_root / "manual_edit_queue")
    process_que_db = MetaDb(paths.project_group_root / "mig_queue")


    build_process_queue(process_que_db)
    rounds = [
        "premig",
        "llmmig",
        "merge_skipped",
        "async_transform",
        "manual_edit",
    ]
    runner = MigRunner(process_que_db, rounds=set(rounds), dry_run=False, use_cache=True, smart_skip_tests=False,
                       remove_repo_after_done=False)
    runner.run_all()


def build_process_queue(queue: MetaDb):
    mig_db = MigDb(paths.mig_db_root)
    migs = mig_db.all_migs()


    # migs = find_migs(migs, mig_id="alanhamlett@pip-update-requirements__e407b929__click__typer")
    # migs = list(premig_not_done(migs))
    # migs = list(migs_round_done(migs, "manual_edit"))
    # migs = migs[50:]
    # migs = find_migs(migs, src="requests", tgt="aiohttp")

    migs = migs_from_ids("""
       abinthomasonline@repopack-py__dc2b9243__colorama__rich
              """)



    lps = {mig.lib_pair for mig in migs}
    print(f"Found {len(migs)} migs with {len(lps)} unique library pairs")
    #
    #migs = list(migs_round_done(migs, 1))

    # migs = migs_from_ids("""
    #    abinthomasonline@repopack-py__dc2b9243__colorama__rich
    #           """)

    queue_migs(queue, migs)


if __name__ == '__main__':
    main()
