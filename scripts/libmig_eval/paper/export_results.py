from pprint import pprint

from libmig_eval.latex.latex_result_data import LatexResultData, percent, format_float, format_percent
from libmig_eval.latex.utils import format_int
from libmig_eval.paper.paper_data import load_per_mig_results
from libmig_eval.util.lib_db import LibPairDb
from libmig_eval.util.meta_db import MetaDb
from libmig_eval.util.mig_db import MigDb
from libmig_eval.util.paths import Paths

_latex_replacements = {
}


def latex_friendly(name: str):
    return _latex_replacements.get(name, name)


# check the export_results file in the previous project to find useful stuff

class ExportResults:
    """
    Guidelines:
    - Results task should not generate any CSV.
    """

    def __init__(self, paths: Paths):
        self.paths = paths
        self.per_mig_results = load_per_mig_results(refresh=False)

    def run(self):
        print("Exporting results...")
        latex_data = LatexResultData(self.paths.paper_root)

        # enable clean to reset the data when a lot of things changed, specially when some results are removed or renamed.
        # disable clean when you want to keep the data and only update the new results. This should be faster.

        # latex_data.clean()

        results = {
            **self.repo_filter_stats(),
            **self.lib_filter_stats(),
            **self.experiment_data_stats(),
            **self.lib_pair_filter_stats(),
            **self.mig_correctness_stats(),
            **self.manual_edit_results(),
        }

        latex_data.update(results)

        pprint(results)

        # ResultsCharts(self.paths, self.experiment_data).draw()

    def repo_filter_stats(self):
        repo_db = MetaDb(self.paths.repo_db_root)
        total_repos = repo_db.count_all()
        large = repo_db.count("excluded.large")
        after_large_filter = total_repos - large

        no_requirements = repo_db.count("excluded.no_requirements_file")
        after_no_req_filter = after_large_filter - no_requirements

        no_tests_by_api = repo_db.count("excluded.no_test_file_by_api")
        after_no_tests_by_api_filter = after_no_req_filter - no_tests_by_api

        timeout = repo_db.count("excluded.timeout")
        after_timeout_filter = after_no_tests_by_api_filter - timeout

        test_not_run = (repo_db.count("excluded.test_not_run") +
                        repo_db.count("excluded.unhandled_error") +
                        repo_db.count("excluded.command_error"))
        after_test_not_run_filter = after_timeout_filter - test_not_run

        low_passing = repo_db.count("excluded.low_passing")
        after_low_passing_filter = after_test_not_run_filter - low_passing

        low_coverage = repo_db.count("excluded.low_coverage")
        after_low_coverage_filter = after_low_passing_filter - low_coverage

        manual_exclude = repo_db.count("excluded.manual")
        after_manual_exclude_filter = after_low_coverage_filter - manual_exclude

        included = repo_db.count("included")

        assert after_manual_exclude_filter == included

        return {
            "seart download date": "January 4, 2025",
            "seart filter min lines": 100,
            "seart filter last commit after": "January 1, 2024",
            "repo seart count": format_int(total_repos),
            "repo excluded large count": format_int(large),
            "repo after large filter count": format_int(after_large_filter),
            "repo excluded no req file count": format_int(no_requirements),
            "repo after no req file filter count": format_int(after_no_req_filter),
            "repo excluded no test file by api count": format_int(no_tests_by_api),
            "repo after no test file by api filter count": format_int(after_no_tests_by_api_filter),
            "repo excluded timeout count": timeout,
            "repo after timeout filter count": after_timeout_filter,
            "repo excluded test not run count": test_not_run,
            "repo after test not run filter count": after_test_not_run_filter,
            "repo excluded low passing count": low_passing,
            "repo after low passing filter count": after_low_passing_filter,
            "repo excluded low coverage count": low_coverage,
            "repo after low coverage filter count": after_low_coverage_filter,
            "repo excluded manual count": manual_exclude,
            "repo after manual filter count": after_manual_exclude_filter,
            "repo included count": included,
        }

    def lib_filter_stats(self):
        lib_db = MetaDb(self.paths.lib_db_root)

        # source libs
        total_libs = lib_db.count_all()

        no_libio = lib_db.count("excluded.not_on_libio")
        after_no_libio_filter = total_libs - no_libio

        too_few_dependents = lib_db.count("excluded.too_few_dependents")
        after_too_few_dependents_filter = after_no_libio_filter - too_few_dependents

        no_description = lib_db.count("excluded.no_description")
        after_no_description_filter = after_too_few_dependents_filter - no_description

        included = lib_db.count("included")
        assert after_no_description_filter == included

        return {
            "source lib candidate count": total_libs,
            "source lib excluded not on libio count": no_libio,
            "source lib after not on libio filter count": after_no_libio_filter,
            "source lib excluded too few dependents count": too_few_dependents,
            "source lib after too few dependents filter count": after_too_few_dependents_filter,
            "source lib excluded no description count": no_description,
            "source lib after no description filter count": after_no_description_filter,
            "source lib included count": included,

        }

    def lib_pair_filter_stats(self):
        lib_pair_db = LibPairDb()
        all_candidates = lib_pair_db.all_candidates()

        all_candidates = len(all_candidates)
        low_freq = len(lib_pair_db.candidate_category("low_frequency"))
        tgt_lib_old = len(lib_pair_db.candidate_category("target_old"))
        non_analogous = len(lib_pair_db.candidate_category("non_analogous"))
        analogous = len(lib_pair_db.candidate_category("analogous"))

        validated = non_analogous + analogous

        assert all_candidates == low_freq + tgt_lib_old + non_analogous + analogous
        return {
            "lib pair candidate count": all_candidates,
            "lib pair low frequency count": low_freq,
            "lib pair old target count": tgt_lib_old,
            "lib pair manually validated count": validated,
            "lib pair non analogous count": non_analogous,
            "lib pair analogous count": analogous,
        }

    def experiment_data_stats(self):
        migs = MigDb(self.paths.mig_db_root).all_migs()
        total_migs = len(migs)

        unique_repos = len({m.repo for m in migs})
        unique_source_libs = len({m.source for m in migs})
        unique_target_libs = len({m.target for m in migs})
        unique_pairs = len({m.lib_pair for m in migs})
        unique_libs = len({m.source for m in migs} | {m.target for m in migs})

        return {
            "mig exp count": total_migs,
            "repo exp count": unique_repos,
            "source lib exp count": unique_source_libs,
            "target lib exp count": unique_target_libs,
            "lib pair exp count": unique_pairs,
            "lib exp count": unique_libs,
        }

    def mig_correctness_stats(self):
        df = self.per_mig_results

        total_migs = len(df)

        # llmmig
        llmmig_correct_count = df[df["llmmig_correctness"].eq(1)].shape[0]
        llmmig_incorrect_count = df[df["llmmig_correctness"].eq(0)].shape[0]
        llmmig_partial_correct_count = df[df["llmmig_correctness"].between(0, 1, "neither")].shape[0]
        llmmig_median_correctness = df["llmmig_correctness"].median()

        # merge skipped
        df_merge = df[df["merge_skipped_has_result"].eq(True)].copy()
        merge_skipped_applied_count = df_merge.shape[0]
        merge_skipped_correct_count = df[df["merge_skipped_correctness"].eq(1)].shape[0]
        merge_skipped_incorrect_count = df[df["merge_skipped_correctness"].eq(0)].shape[0]
        merge_median_correctness = df["merge_skipped_correctness"].median()

        merge_skipped_improved = df_merge[df_merge["merge_skipped_abs_improvement"].gt(0)].shape[0]
        merge_median_improvement = df_merge["merge_skipped_rel_improvement"].median()
        merge_mean_improvement = df_merge["merge_skipped_rel_improvement"].mean()

        # async transform
        df_async = df[df["async_transform_has_result"].eq(True)].copy()
        async_transform_applied_count = df_async.shape[0]
        async_transform_correct_count = df[df["async_transform_correctness"].eq(1)].shape[0]
        async_transform_incorrect_count = df[df["async_transform_correctness"].eq(0)].shape[0]
        async_median_correctness = df["async_transform_correctness"].median()

        async_transform_improved = df_async[df_async["async_transform_abs_improvement"].gt(0)].shape[0]
        async_transform_median_improvement = df_async["async_transform_rel_improvement"].median()
        async_transform_mean_improvement = df_async["async_transform_rel_improvement"].mean()

        # overall correctness
        overall_correct_count = df[df["overall_correctness"].eq(1)].shape[0]
        overall_part_correct_count = df[df["overall_correctness"].between(0, 1, "neither")].shape[0]
        overall_incorrect_count = df[df["overall_correctness"].eq(0)].shape[0]

        all_manual_fix_migs = df[df["overall_correctness"].lt(1)]
        mig_need_manual_fix_count = all_manual_fix_migs.shape[0]
        lp_need_manual_fix_count = all_manual_fix_migs["lib_pair_id"].nunique()
        repo_need_manual_fix_count = all_manual_fix_migs["repo_id"].nunique()

        median_correctness = df["overall_correctness"].median()

        return {
            # llmmig
            "mig LLMMig correct count": llmmig_correct_count,
            "mig LLMMig correct percent": percent(llmmig_correct_count, total_migs),
            "mig LLMMig incorrect count": llmmig_incorrect_count,
            "mig LLMMig incorrect percent": percent(llmmig_incorrect_count, total_migs),
            "mig LLMMig partial correct count": llmmig_partial_correct_count,
            "mig LLMMig partial correct percent": percent(llmmig_partial_correct_count, total_migs),
            "mig LLMMig median correctness": percent(llmmig_median_correctness),
            # merge skipped
            "mig MergeSkipped applied count": merge_skipped_applied_count,
            "mig MergeSkipped applied percent": percent(merge_skipped_applied_count, total_migs),
            "mig MergeSkipped improved count": merge_skipped_improved,
            "mig MergeSkipped improved percent": percent(merge_skipped_improved, merge_skipped_applied_count),
            "mig MergeSkipped correct count": merge_skipped_correct_count,
            "mig MergeSkipped correct percent": percent(merge_skipped_correct_count, total_migs),
            "mig MergeSkipped incorrect count": merge_skipped_incorrect_count,
            "mig MergeSkipped incorrect percent": percent(merge_skipped_incorrect_count, total_migs),
            "mig MergeSkipped median correctness": percent(merge_median_correctness),
            "mig MergeSkipped median improvement": percent(merge_median_improvement),
            "mig MergeSkipped mean improvement": percent(merge_mean_improvement),
            # async transform
            "mig AsyncTransform correct count": async_transform_correct_count,
            "mig AsyncTransform correct percent": percent(async_transform_correct_count, total_migs),
            "mig AsyncTransform incorrect count": async_transform_incorrect_count,
            "mig AsyncTransform incorrect percent": percent(async_transform_incorrect_count, total_migs),
            "mig AsyncTransform applied count": async_transform_applied_count,
            "mig AsyncTransform applied percent": percent(async_transform_applied_count, total_migs),
            "mig AsyncTransform improved count": async_transform_improved,
            "mig AsyncTransform improved percent": percent(async_transform_improved, async_transform_applied_count),
            "mig AsyncTransform median correctness": percent(async_median_correctness),
            "mig AsyncTransform median improvement": percent(async_transform_median_improvement),
            "mig AsyncTransform mean improvement": percent(async_transform_mean_improvement),
            # other
            "mig Overall correct count": overall_correct_count,
            "mig Overall correct percent": percent(overall_correct_count, total_migs),
            "mig Overall partial correct count": overall_part_correct_count,
            "mig Overall partial correct percent": percent(overall_part_correct_count, total_migs),
            "mig Overall incorrect count": overall_incorrect_count,
            "mig Overall incorrect percent": percent(overall_incorrect_count, total_migs),
            "mig Overall need manual fix count": mig_need_manual_fix_count,
            "mig Overall need manual fix percent": percent(mig_need_manual_fix_count, total_migs),
            "mig Overall median correctness": percent(median_correctness, 1),

            "LibPair need manual fix count": lp_need_manual_fix_count,
            "repo need manual fix count": repo_need_manual_fix_count,
        }

    def manual_edit_results(self):
        df = self.per_mig_results

        man = df[df["manual_edit_has_result"].eq(True)]

        manual_fix_applied = man.shape[0]
        manual_fix_corrected = man[man["manual_edit_correctness"].eq(1)].shape[0]
        manual_fix_improved = man[man["manual_edit_abs_improvement"].gt(0)].shape[0]

        median_correctness = man["manual_edit_correctness"].median()

        repo_manual_fix_applied = man["repo_id"].nunique()

        migloc_auto_avg = df["premig_to_best_migloc"].mean()
        migloc_manual_avg = df["best_to_manual_edit_migloc"].mean()

        migloc_auto_min = df["premig_to_best_migloc"].min()
        migloc_manual_min = df["best_to_manual_edit_migloc"].min()
        migloc_auto_max = df["premig_to_best_migloc"].max()
        migloc_manual_max = df["best_to_manual_edit_migloc"].max()

        migloc_auto_median = df["premig_to_best_migloc"].median()
        migloc_manual_median = df["best_to_manual_edit_migloc"].median()
        dev_effort_saving_median = df["dev_effort_saving"].median()

        return {
            "mig manual fix applied": manual_fix_applied,
            "mig manual fix corrected": manual_fix_corrected,
            "mig manual fix corrected percent": percent(manual_fix_corrected, manual_fix_applied),
            "mig manual fix not corrected": manual_fix_applied - manual_fix_corrected,
            "mig manual fix not corrected percent": percent(manual_fix_applied - manual_fix_corrected, manual_fix_applied),
            "mig manual fix improved": manual_fix_improved,
            "mig manual fix improved percent": percent(manual_fix_improved, manual_fix_applied),
            "mig manual fix median correctness": format_float(median_correctness),
            "repo manual fix applied": repo_manual_fix_applied,
            "migloc auto median": format_int(migloc_auto_median),
            "migloc manual median": format_int(migloc_manual_median),
            "migloc auto median percent": percent(dev_effort_saving_median),
            "migloc manual median percent": percent(1 - dev_effort_saving_median),
            "migloc auto avg": format_int(migloc_auto_avg),
            "migloc manual avg": format_int(migloc_manual_avg),
            "migloc auto min": format_int(migloc_auto_min),
            "migloc manual min": format_int(migloc_manual_min),
            "migloc auto max": format_int(migloc_auto_max),
            "migloc manual max": format_int(migloc_manual_max),
        }


def export_results():
    paths = Paths()
    ExportResults(paths).run()


if __name__ == '__main__':
    export_results()
