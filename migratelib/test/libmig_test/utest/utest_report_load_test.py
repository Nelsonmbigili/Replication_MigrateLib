import json

from libmig.utest.utest_report import *
from pathlib import Path


def test_load():
    data = json.load(Path("test/test_data/report-1.json").resolve().absolute().open())
    report = UTestReport.load(data)

    assert isinstance(report, UTestReport)
    assert isinstance(report.summary, UTestSummary)
    assert isinstance(report.collectors, list)
    assert isinstance(report.collectors[0], UTestCollector)

    assert isinstance(report.tests, list)
    assert isinstance(report.tests[0], UTestItem)
    assert isinstance(report.tests[0].call, UTestItemResult)
    assert isinstance(report.tests[0].setup, UTestItemResult)
    assert isinstance(report.tests[0].teardown, UTestItemResult)

    assert isinstance(report.warnings, list)
    assert isinstance(report.warnings[0], UTestWarning)
