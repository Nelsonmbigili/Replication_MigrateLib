from libmig.utest import UTestReport


def passed_tests(round_test_report: UTestReport):
    return round_test_report.summary.passed


def correctness(premig_test_report: UTestReport, round_test_report: UTestReport):
    premig_passed = set(test.nodeid for test in premig_test_report.tests if test.passed)
    postmig_passed = set(test.nodeid for test in round_test_report.tests if test.passed)

    if not premig_passed:
        raise ValueError("No tests passed in the pre-migration report.")

    return len(postmig_passed.intersection(premig_passed)) / len(premig_passed)


def abs_improvement(llmmig_test_report: UTestReport, round_test_report: UTestReport):
    return round_test_report.summary.passed - llmmig_test_report.summary.passed


def rel_improvement(llmmig_test_report: UTestReport, round_test_report: UTestReport):
    if llmmig_test_report.summary.passed == 0:
        if round_test_report.summary.passed == 0:
            return 0
        return 1
    return abs_improvement(llmmig_test_report, round_test_report) / llmmig_test_report.summary.passed
