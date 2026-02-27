from pytest import fixture
from libmig.utest.utest_report import *
from libmig.utest.utest_report_diff import UTestReportDiff


@fixture
def empty_reports():
    left = UTestReport(
        exitcode=0,
        summary=UTestSummary(passed=0, total=0, collected=0),
        collectors=[],
        tests=[],
        warnings=[]
    )

    right = UTestReport(
        exitcode=0,
        collectors=[],
        summary=UTestSummary(passed=0, total=0, collected=0),
        tests=[],
        warnings=[]
    )

    return left, right


def add_test_item(report: UTestReport, node_id: str, outcome: str):
    report.tests.append(UTestItem(
        nodeid=node_id,
        lineno=1,
        outcome=outcome,
        keywords=[],
        call=UTestItemResult(outcome=outcome),
        setup=UTestItemResult(outcome=outcome),
        teardown=UTestItemResult(outcome=outcome)
    ))
    report.summary.total += 1
    if outcome == "passed":
        report.summary.passed += 1
    report.summary.collected += 1


def test_utest_report_diff__identical__no_diff(empty_reports):
    left, right = empty_reports
    diff = UTestReportDiff(left, right)
    assert len(diff.diffs) == 0


def test_utest_report_diff__lef_has_more_than_right(empty_reports):
    left, right = empty_reports
    add_test_item(left, "abc", "passed")
    diff = UTestReportDiff(left, right)

    assert len(diff.diffs) == 1
    assert diff.diffs[0].test_id == "abc"
    assert diff.diffs[0].outcome_before == "passed"
    assert diff.diffs[0].outcome_after == "not found"


def test_utest_report_diff__right_has_more_than_left(empty_reports):
    left, right = empty_reports
    add_test_item(right, "abc", "passed")
    diff = UTestReportDiff(left, right)

    assert len(diff.diffs) == 1
    assert diff.diffs[0].test_id == "abc"
    assert diff.diffs[0].outcome_before == "not found"
    assert diff.diffs[0].outcome_after == "passed"


def test_utest_report_diff__left_pass_right_fail(empty_reports):
    left, right = empty_reports
    add_test_item(left, "abc", "passed")
    add_test_item(right, "abc", "failed")
    diff = UTestReportDiff(left, right)

    assert len(diff.diffs) == 1
    assert diff.diffs[0].test_id == "abc"
    assert diff.diffs[0].outcome_before == "passed"
    assert diff.diffs[0].outcome_after == "failed"


def test_utest_report_diff__left_fail_right_pass(empty_reports):
    left, right = empty_reports
    add_test_item(left, "abc", "failed")
    add_test_item(right, "abc", "passed")
    diff = UTestReportDiff(left, right)

    assert len(diff.diffs) == 1
    assert diff.diffs[0].test_id == "abc"
    assert diff.diffs[0].outcome_before == "failed"
    assert diff.diffs[0].outcome_after == "passed"


def test_utest_report_diff__different_test_ids(empty_reports):
    left, right = empty_reports
    add_test_item(left, "abc", "passed")
    add_test_item(right, "xyz", "failed")
    diff = UTestReportDiff(left, right)

    assert len(diff.diffs) == 2
    abc = diff.diff_index["abc"]
    xyz = diff.diff_index["xyz"]
    assert abc.outcome_before == "passed"
    assert abc.outcome_after == "not found"
    assert xyz.outcome_before == "not found"
    assert xyz.outcome_after == "failed"
