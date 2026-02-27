import pandas as pd

from libmig_eval.config import MODEL_CODE
from libmig_eval.util.mig_db import MigDb
from libmig_eval.util.models import Mig
from libmig_eval.util.paths import Paths

paths = Paths()


class MigSummarizer:

    def __init__(self, migs: list[Mig]):
        self.migs = migs

    def _coverage(self, result: dict):
        total_lines = 0
        cov_lines = 0
        for file, file_data in result.get("files", {}).items():
            cov = file_data.get("change_coverage", {})
            total_lines += len(cov)
            cov_lines += sum(1 for line, covered in cov.items() if covered)

        return f"{(cov_lines / total_lines if total_lines else 0):.0%}"

    def _r2_summary_cells(self, r2_result: dict, r1_results: dict, r2_type: str):
        if r2_result["status"] == "error":
            return {f"r2 {r2_type} status": r2_result.get("error code", "error")}

        cells = {f"r2 {r2_type} status": r2_result["status"]}
        r2_summary = r2_result.get("summary", {})

        cells.update({f"r2 {r2_type} {k}": v for k, v in r2_summary.items()})
        cells[f"r2 {r2_type} mig cov"] = self._coverage(r2_result)
        cells[f"r2 {r2_type} improvement"] = r1_results["summary"]["total diff"] - r2_summary["total diff"]
        return cells

    def _mig_summary_row(self, mig: Mig):
        row = {
            "mig_id": mig.id,
            "repo": mig.repo,
            "commit": mig.commit,
            "source": mig.source,
            "target": mig.target,
            "report_generated": False,
        }
        mig_report = paths.load_mig_report(mig)

        if not mig_report:
            return row

        row["report_generated"] = True

        premig_round = mig_report.premig
        llmmig_round = mig_report.llmmig
        merge_round = mig_report.merge_skipped
        async_round = mig_report.async_transform
        row["premig_done"] = False

        if premig_round:
            row["source_version"] = premig_round.source_version
            row["target_version"] = premig_round.target_version
            row["premig_done"] = True
            row["premig_status"] = premig_round.status if premig_round.status != "error" else premig_round.error_type
            row["premig_cov"] = premig_round.project_coverage
            row["total_tests"] = premig_round.total_tests
            row["premig_passed_tests"] = premig_round.passed_tests

            if llmmig_round:
                row["llmmig_done"] = True
                row[
                    "llmmig_status"] = llmmig_round.status if llmmig_round.status != "error" else llmmig_round.error_type
                if llmmig_round.status != "error":
                    row["llmmig_cov"] = llmmig_round.project_change_coverage
                    row["llmmig_total_diff"] = len(llmmig_round.test_diffs)

                if merge_round:
                    row["merge_done"] = True
                    row["merge_status"] = merge_round.status if merge_round.status != "error" else merge_round.error_type
                    if merge_round.status == "finished":
                        row["merge_cov"] = merge_round.project_change_coverage
                        row["merge_total_diff"] = len(merge_round.test_diffs)
                        row["merge_improvement"] = len(llmmig_round.test_diffs) - len(merge_round.test_diffs)

                if async_round:
                    row["async_done"] = True
                    row["async_status"] = async_round.status if async_round.status != "error" else async_round.error_type
                    row["async_base_round"] = async_round.base_round
                    if async_round.status == "finished":
                        row["async_cov"] = async_round.project_change_coverage
                        row["async_total_diff"] = len(async_round.test_diffs)
                        row["async_improvement"] = len(llmmig_round.test_diffs) - len(async_round.test_diffs)

                best_round = mig_report.get_best_round()
                if best_round:
                    row["best_round"] = best_round

        return row

    def summarize(self, migs: list[Mig]):
        rows = []
        for i, mig in enumerate(migs, start=1):
            print(f"{i}/{len(migs)}: {mig.id}")
            row = self._mig_summary_row(mig)
            if row:
                rows.append(row)

        df = pd.DataFrame(rows)
        out_path = paths.results_root / f"mig-summaries.{MODEL_CODE}.csv"
        df.to_csv(out_path, index=False)
        print(f"Mig summaries written to {out_path}")

        print(f"premig status summary: total {len(df)} migs")
        print(df["premig_status"].value_counts(dropna=False))


def main():
    migs = MigDb(paths.mig_db_root).all_migs()
    MigSummarizer(migs).summarize(migs)


if __name__ == '__main__':
    main()
