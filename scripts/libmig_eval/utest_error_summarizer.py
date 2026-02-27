import json
from pathlib import Path

import pandas as pd

from libmig_eval.util.models import decode_mig_id
from libmig_eval.util.paths import Paths


class UTestErrorSummarizer:
    def __init__(self, results_root: Path):
        self.results_root = results_root

    def summarize(self):
        # pattern: <org>@<repo>__<commit>__<src>__<tgt>/1/test-report.json
        test_report_files: list[Path] = list(self.results_root.rglob("*@*__*__*__*/1/test-report.json"))
        print(f"Found {len(test_report_files)} test reports")

        rows = []
        for test_report_file in test_report_files:
            report = json.load(test_report_file.open())

            mig_id = test_report_file.parent.parent.name
            repo, commit, src, tgt = decode_mig_id(mig_id)

            failed_tests = [tst for tst in report["tests"] if
                            "call" in tst and tst["call"]["outcome"] == "failed"]
            for failed_test in failed_tests:
                message = failed_test["call"]['crash']['message']
                error = failed_test["call"]["traceback"][-1]["message"]
                rows.append({
                    "mig": mig_id,
                    "repo": repo,
                    "commit": commit,
                    "src": src,
                    "tgt": tgt,
                    "test_id": failed_test["nodeid"],
                    "error": error,
                    "message": message
                })

        out_file = self.results_root.parent / f"error-summaries.{self.results_root.name}.csv"
        pd.DataFrame(rows).to_csv(out_file, index=False)


if __name__ == '__main__':
    UTestErrorSummarizer(Paths().project_group_root / "libmig-eval-results" / "libmig_out.4omini").summarize()
