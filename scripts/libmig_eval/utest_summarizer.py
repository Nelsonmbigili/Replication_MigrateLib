import pandas as pd
import yaml

from libmig_eval.util.mig_db import MigDb
from libmig_eval.util.models import Mig
from libmig_eval.util.paths import Paths

paths = Paths()


class UTestSummarizer:
    def __init__(self, migs: list[Mig]):
        self.migs = migs

    def summarize(self):
        rows = []
        for mig in self.migs:
            result_file = paths.mig_result_file_path(mig, "1-first")
            if not result_file.exists():
                print(f"Skipping. No results found at {result_file.as_posix()}")
                continue

            results = yaml.safe_load(result_file.open(encoding="utf-8"))
            utest_diffs = results.get("diffs", {})
            if not utest_diffs:
                print(f"Skipping. No test diffs found for {mig.id}")
                continue

            print(f"Summarizing {mig.id}")
            for test_id, diff in utest_diffs.items():
                row = mig.to_dict()
                row["test_id"] = test_id
                row.update(diff)
                rows.append(row)

        out_file = paths.results_root / "test-summaries.csv"
        pd.DataFrame(rows).to_csv(out_file, index=False)
        print(f"Test summaries written to {out_file}")


def main():
    migs = MigDb(paths.migs_csv_path).all_migs()
    summarizer = UTestSummarizer(migs)
    summarizer.summarize()


if __name__ == '__main__':
    main()
