from libmig_eval.mig_filter import not_correct, sample_migs, queue_migs
from libmig_eval.util import Paths
from libmig_eval.util.mig_db import MigDb

paths = Paths()


def sample_manual_edit():
    """
    Select a subset of migrations from the incorrect ones such that:
    1. One migration per library pair
    2. As many unique repos as possible
    :return:
    """
    confirm = input("This will clear the previous queue and create a new list of migrations that need manual edit."
                    " Do you want to continue? (y/n): ")
    if confirm.lower() != "y":
        print("Exiting...")
        return

    migs = MigDb(paths.mig_db_root).all_migs()
    non_correct_reports = list(not_correct(migs))
    selected_migs = sample_migs(non_correct_reports)

    lib_pairs = {mig.lib_pair_id for mig in non_correct_reports}
    unique_sources = {mig.source for mig in non_correct_reports}
    unique_targets = {mig.target for mig in non_correct_reports}
    unique_libs = unique_sources.union(unique_targets)
    repos = {mig.repo_id for mig in non_correct_reports}
    print(f"Total non-correct reports: {len(non_correct_reports)}")
    print(f"Unique lib pairs: {len(lib_pairs)}")
    print(f"Unique repos: {len(repos)}")
    print(f"Unique libs: {len(unique_libs)}")
    print(f"Unique sources: {len(unique_sources)}")
    print(f"Unique targets: {len(unique_targets)}")

    print(f"Selected migrations: {len(selected_migs)}")
    print(f"Unique lib pairs: {len({mig.lib_pair_id for mig in selected_migs})}")
    print(f"Unique repos: {len({mig.repo_id for mig in selected_migs})}")

    queue_migs(selected_migs, "manual_edit_queue")
    print(*sorted(f"{mig.lib_pair_id}:{mig.repo_id}" for mig in selected_migs), sep="\n")
