import pandas as pd
from libmig.metrics.migloc import mig_loc
from libmig.mig.mig_report_models import RoundName, MigReport, AllMigRoundNames
from libmig.mig.mig_round_paths import MigRoundPaths, create_round_path
from libmig.utils.cache import read_cache

from libmig_eval.paper.metrics import *
from libmig_eval.util import Paths, Mig
from libmig_eval.util.mig_db import MigDb

paths = Paths()


def _update_round_result(mig: Mig, round_name: RoundName, full_report: MigReport, premig_test_report: UTestReport,
                         result: dict[str, any]):
    round_report = full_report.get_round_report(round_name)
    has_result = round_report and round_report.has_results()

    passed_tests_count = -1
    round_correctness = -1
    round_abs_improvement = -1
    round_rel_improvement = -1

    if has_result:
        utest_report = paths.load_test_report(mig, round_name)
        passed_tests_count = passed_tests(utest_report)
        round_correctness = correctness(premig_test_report, utest_report)

        if round_name != "llmmig":
            base_round_utest_report = paths.load_test_report(mig, round_report.base_round)
            round_abs_improvement = abs_improvement(base_round_utest_report, utest_report)
            round_rel_improvement = rel_improvement(base_round_utest_report, utest_report)

    result.update({
        f"{round_name}_has_result": has_result,
        f"{round_name}_passed_tests": passed_tests_count,
        f"{round_name}_correctness": round_correctness,
        f"{round_name}_abs_improvement": round_abs_improvement,
        f"{round_name}_rel_improvement": round_rel_improvement,
    })
    return has_result


def _update_metric_results(mig: Mig, full_report: MigReport, result: dict[str, any]):
    """Must run after all _update_round_result"""
    manual_edit_result = full_report.manual_edit

    # migloc
    best_round = full_report.get_best_round(prefer_later_when_equal=True, rounds=["merge_skipped", "async_transform"])
    best_round = best_round or "llmmig"
    premig_paths = create_round_path(paths.mig_out_path(mig), "premig")
    best_base = premig_paths if best_round == "llmmig" else create_round_path(paths.mig_out_path(mig), "llmmig",
                                                                              base=premig_paths)

    best_round_paths = create_round_path(paths.mig_out_path(mig), best_round, base=best_base)
    premig_to_best_loc = mig_loc(premig_paths, best_round_paths)
    result["premig_to_best_migloc"] = premig_to_best_loc

    # best to manual edit
    manual_edit_paths = create_round_path(paths.mig_out_path(mig), "manual_edit")
    best_to_manual_edit_loc = mig_loc(best_round_paths, manual_edit_paths)
    result["best_to_manual_edit_migloc"] = best_to_manual_edit_loc

    if not manual_edit_result or not manual_edit_result.has_results():
        return

    manual_edit_improvement = result.get("manual_edit_rel_improvement", -1)
    if manual_edit_improvement <= 0:
        return  # No improvement, therefore, exclude from metrics

    result["dev_effort_saving"] = premig_to_best_loc / (premig_to_best_loc + best_to_manual_edit_loc)


def _one_mig_result(mig: Mig):
    full_report = Paths().load_mig_report(mig)
    result: dict[str, any] = {**mig.to_dict(), "repo_id": mig.repo_id, "lib_pair_id": mig.lib_pair_id}

    premig_test_report = paths.load_test_report(mig, "premig")
    result["total_tests"] = premig_test_report.summary.total
    result["premig_passed_tests"] = premig_test_report.summary.passed

    _update_round_result(mig, "llmmig", full_report, premig_test_report, result)
    _update_round_result(mig, "merge_skipped", full_report, premig_test_report, result)
    _update_round_result(mig, "async_transform", full_report, premig_test_report, result)

    all_correctness = [result[f"{rn}_correctness"] for rn in AllMigRoundNames]
    result["overall_correctness"] = max(all_correctness)

    best_round = full_report.get_best_round()
    result["best_round"] = best_round

    _update_round_result(mig, "manual_edit", full_report, premig_test_report, result)

    _update_metric_results(mig, full_report, result)

    return result


def load_per_mig_results(refresh=False):
    """
    Load the results data from the cache or generate it if it does not exist.
    :param refresh: if True, regenerate the data even if it exists in the cache
    :return:
    """
    paths = Paths()
    cache_file_path = paths.eval_project_root / "data" / "per-mig-results.cache.csv"
    if not refresh and cache_file_path.exists():
        df = read_cache(cache_file_path, format="csv")
    else:
        print("Generating per-mig results data. Can take a while. Use refresh=False to load from cache.")
        migs = MigDb(paths.mig_db_root).all_migs()
        mig_results = []

        for i, mig in enumerate(migs, start=1):
            # if mig.id != "funilrys@pyfunceble__a2756c4f__python-dotenv__environs":
            #     continue
            print(f"Processing mig {i}/{len(migs)}: {mig.id}")
            one_result = _one_mig_result(mig)
            mig_results.append(one_result)

        df = pd.DataFrame(mig_results)
        df.to_csv(cache_file_path, index=False)

    df["merge_skipped_correctness"] = df["merge_skipped_correctness"].mask(
        df["merge_skipped_correctness"] < df["llmmig_correctness"],
        df["llmmig_correctness"]
    )

    # if async transform reduced correctness, we keep the llmmig correctness
    df["async_transform_correctness"] = df["async_transform_correctness"].mask(
        df["async_transform_correctness"] < df["merge_skipped_correctness"],
        df["merge_skipped_correctness"]
    )

    return df
