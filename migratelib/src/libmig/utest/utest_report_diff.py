from libmig.mig.mig_report_models import UTestDiffReport
from libmig.utest import UTestReport, UTestItem


class UTestItemDiff:
    """
    Diff between two UTestItem objects
    """

    def __init__(self, test_id: str, before: UTestItem | None, after: UTestItem | None):
        self.test_id = test_id
        self.before = before
        self.after = after

        self.outcome_before = before.outcome if before is not None else "not found"
        self.outcome_after = after.outcome if after is not None else "not found"

        assert self.outcome_before != self.outcome_after

    def __str__(self):
        return f"{self.test_id}: {self.outcome_before} != {self.outcome_after}"

    @property
    def utest_file(self):
        return self.test_id.split("::")[0]

    @property
    def utest_name(self):
        return self.test_id.split("::")[-1]

    def as_report(self):
        if self.outcome_after == "skipped":
            # some cases, the previous tests passed but the new test is skipped. Specially when asyncio is introduced
            exception = "the test was skipped"
            error_message = ""
            failed_phase_name = ""
        elif self.after is not None:
            exception = self.after.error_type
            error_message = self.after.failed_phase.crash.message if self.after.failed_phase.crash else "unknown"
            failed_phase_name = self.after.failed_phase_name
        else:
            exception = ""
            error_message = ""
            failed_phase_name = "collection"

        return UTestDiffReport(self.test_id, self.outcome_before, self.outcome_after,
                               failed_phase=failed_phase_name, exception=exception, error_message=error_message)


class UTestReportDiff:
    """
    Get diff between two UTestReport objects
    """

    def __init__(self, before: UTestReport, after: UTestReport):
        self.before = before
        self.after = after
        self.diffs: list[UTestItemDiff] = []
        self._calculate_test_diff()
        self.diff_index = {diff.test_id: diff for diff in self.diffs}

    def _calculate_test_diff(self):
        before_tests = {tst.nodeid: tst for tst in self.before.tests}
        after_tests = {tst.nodeid: tst for tst in self.after.tests}

        all_test_ids = set(before_tests.keys()) | set(after_tests.keys())

        for test_id in all_test_ids:
            btest = before_tests.get(test_id, None)
            atest = after_tests.get(test_id, None)

            if btest is not None and btest.outcome != "passed":
                # if the test is not passed, we don't care about the diff
                continue
            if btest is None or atest is None or btest.outcome != atest.outcome:
                self.diffs.append(UTestItemDiff(test_id, btest, atest))

        self.diffs.sort(key=lambda diff: diff.test_id)
        self.summary = {
            "total tests": len(all_test_ids),
            "total diff": len(self.diffs),
        }
