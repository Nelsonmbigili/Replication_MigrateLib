from random import random

from libmig.mig.mig_report_models import load_report, RoundName

from libmig_eval.util import Mig, Paths, delete_dir
from libmig_eval.util.meta_db import MetaDb

paths = Paths()


def queue_migs(queue: MetaDb, migs: list[Mig]):
    delete_dir(queue.db_root / "queued")
    delete_dir(queue.db_root / "running")
    delete_dir(queue.db_root / "error")
    delete_dir(queue.db_root / "done")

    print(f"Adding {len(migs)} migs to the queue")
    for mig in migs:
        meta = mig.to_dict()
        queue.save("queued", meta)

    return queue


def find_migs(migs: list[Mig], repo: str = None, src: str = None, tgt: str = None, mig_id: str = None):
    if mig_id:
        migs = [mig for mig in migs if mig.id == mig_id]
    if repo:
        migs = [mig for mig in migs if mig.repo == repo]
    if src:
        migs = [mig for mig in migs if mig.source == src]
    if tgt:
        migs = [mig for mig in migs if mig.target == tgt]
    return migs


def migs_round_done(migs: list[Mig], round_name: RoundName):
    for mig in migs:
        report_path = paths.mig_out_path(mig).joinpath("report.yaml")
        if not report_path.exists():
            continue
        report = load_report(report_path)
        round_report = report.get_round_report(round_name)
        if not round_report:
            continue
        if round_report.status != "finished":
            continue
        yield mig


def premig_not_done(migs: list[Mig]):
    for mig in migs:
        report_path = paths.mig_out_path(mig).joinpath("report.yaml")
        if not report_path.exists():
            yield mig
        else:
            report = load_report(report_path)
            if not report.premig.is_finished() or report.premig.passed_tests is None:
                yield mig


def premig_done(migs: list[Mig]):
    for mig in migs:
        report_path = paths.mig_out_path(mig).joinpath("report.yaml")
        if not report_path.exists():
            continue
        report = load_report(report_path)
        if report.premig.is_finished() and report.premig.passed_tests is not None:
            yield mig


def not_correct(migs: list[Mig]):
    for mig in migs:
        mig_result = paths.load_mig_report(mig)
        best_round_name = mig_result.get_best_round() or "llmmig"
        best_round = mig_result.get_round_report(best_round_name)
        if best_round.error_message and best_round.error_message == "no files to migrate":
            print(f"Skipping {mig.id} because no files to migrate")
            continue

        if best_round.test_diffs:
            yield mig


def sample_migs(migs: list[Mig]) -> list[Mig]:
    """
    Sample such a way that:
    - All library pairs are included at least once
    - The repos are as diverse as possible
    :param migs:
    :return:
    """
    migs = sorted(migs, key=lambda mig: f"{mig.repo_id}__{random()}")
    included_libpairs = set()
    included_migs = set()

    all_lib_pairs = {mig.lib_pair for mig in migs}

    i = 0
    while all_lib_pairs != included_libpairs:
        i += 1
        last_included_repo = None
        for mig in migs:
            if mig.repo_id == last_included_repo:
                continue
            if mig in included_migs:
                continue
            if mig.lib_pair in included_libpairs:
                continue

            last_included_repo = mig.repo_id
            included_migs.add(mig)
            included_libpairs.add(mig.lib_pair)

    print(f"Sampled {len(included_migs)}/{len(migs)} migs")
    print(f" in {len({mig.repo_id for mig in included_migs})}/{len({mig.repo_id for mig in migs})} unique repos")
    print(f" in {len(included_libpairs)}/{len(all_lib_pairs)} unique lib pairs")

    return list(included_migs)
