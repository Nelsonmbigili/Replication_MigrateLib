from datetime import datetime

from libmig.mig.mig_error import ErrorCode
from libmig.mig.mig_report_models import PremigRoundReport
from libmig.project import Project
from libmig.utils.venv_installer import install_project_venv


class PremigWorkflow:
    def __init__(self, project: Project):
        self.project = project
        self.log = project.get_loger()

    def run(self):
        src_version, tgt_version = install_project_venv(self.project)

        def _error_report(error_code, error_type):
            return PremigRoundReport("premig", status="error", project_coverage=total_coverage,
                                     error_code=error_code, error_type=error_type, source_version=src_version,
                                     target_version=tgt_version)

        project = self.project
        premig_paths = self.project.premig_paths

        if self.should_skip_tests():
            pass
        else:
            project.run_tests(premig_paths, True)

        utest_report = premig_paths.read_utest_report()

        report = project.get_report()

        cov_report = premig_paths.read_cov_report()
        total_coverage = cov_report["totals"]["percent_covered"]

        if not utest_report.has_tests:
            premig_report = _error_report(error_code=ErrorCode.NO_PREMIG_TESTS.value, error_type="no premig tests")
        elif not utest_report.has_running_tests:
            premig_report = _error_report(error_code=ErrorCode.NO_RUNNING_PREMIG_TESTS.value,
                                          error_type="no running premig tests")
        else:
            premig_report = PremigRoundReport(
                name="premig",
                status="finished",
                source_version=src_version,
                target_version=tgt_version,
                project_coverage=total_coverage,
                total_tests=len(utest_report.tests),
                passed_tests=len(utest_report.passed_tests()))

        premig_report.finished_at = datetime.now().isoformat(sep=" ", timespec="seconds")
        report.premig = premig_report
        project.save_report()

    def should_skip_tests(self):
        premig_paths = self.project.premig_paths
        return (self.project.smart_skip_tests and
                premig_paths.utest_report.exists() and
                premig_paths.cov_report.exists())
