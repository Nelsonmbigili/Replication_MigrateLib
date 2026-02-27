import shutil
from pathlib import Path

from openai import project

from libmig.mig.inferred_async_transform_workflow import InferredAsyncTransformWorkflow
from libmig.mig.llmmig_workflow import LLMMigWorkflow
from libmig.mig.manual_edit_workflow import ManualEditWorkflow
from libmig.mig.mig_error import MigError, ErrorCode
from libmig.mig.mig_report_models import RoundName, AllRoundNames, MigRoundFileReport, MigRoundReport
from libmig.mig.premig_workflow import PremigWorkflow
from libmig.mig.skipped_code_merge_workflow import SkippedCodeMergeWorkflow
from libmig.project import Project
from libmig.utest import UTestReportDiff
from libmig.utils import safe_div
from libmig.utils.file_diff import compute_diff
from libmig.utils.line_range import LineRange


class LibMigRunner:
    def __init__(self, project: Project):
        self.project = project
        self.mig_log = self.project.get_loger()

    def _is_prerequisites_finished(self, round_to_run: RoundName):
        full_report = self.project.get_report()

        # check if all rounds before the round_to_run was successful
        for r_name in AllRoundNames:
            if r_name == round_to_run:
                # did not raise any error, so all previous rounds are done
                return True

            r_report = full_report.get_round_report(r_name)
            if not r_report:
                raise MigError(ErrorCode.PREVIOUS_ROUND_NOT_DONE, f"round {r_name} not done.",
                               f"Round {r_name} not done. Cannot run round {round_to_run}")
            if r_report.status == "error" and r_report.error_code != ErrorCode.TESTS_RUN_INDEFINITELY:
                raise MigError(ErrorCode.PREVIOUS_ROUND_FAILED, f"round {r_name} failed",
                               f"Round {r_name} failed. Cannot run round {round_to_run}")

    def _should_run_round(self, round_name: RoundName):
        full_report = self.project.get_report()
        if round_name not in self.project.rounds:
            print(f"Round {round_name} not configured to run, skipping.")
            return False
        round_report = full_report.get_round_report(round_name)
        if round_report and round_report.is_finished() and not self.project.force_rerun:
            print(f"Round {round_name} already finished, skipping.")
            return False

        return True

    def _base_round_has_test_diff(self, this_round_name: RoundName, base_round_name: RoundName):
        full_report = self.project.get_report()
        round_report = full_report.get_round_report(base_round_name)
        if round_report.test_diffs or round_report.error_code == ErrorCode.TESTS_RUN_INDEFINITELY:
            return True

        print(f"Round {base_round_name} has no test diff, skipping {this_round_name}.")
        return False

    def copy_to_premig(self, files: list[str]):
        """Copy files to the round's files directory ONLY IF IT DOESN'T EXIST."""
        git_repo = self.project.git
        for file in files:
            target_path = self.project.premig_paths.code_file(file)
            if target_path.exists():
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(git_repo.file_path(file), target_path)

    def run(self):
        self.init_output()

        if self._should_run_round("premig"):
            self.run_premig_workflow()

        if self._should_run_round("llmmig"):
            self.run_llmmig_workflow()

        if self._should_run_round("merge_skipped"):
            self.run_merge_workflow()

        if self._should_run_round("async_transform"):
            self.run_async_workflow()

        if self._should_run_round("manual_edit"):
            self.run_manual_edit_workflow()

    def run_premig_workflow(self):
        project = self.project
        self.mig_log.log_event(f"Running premig", "h2")
        workflow = PremigWorkflow(self.project)
        project.git_reset()
        workflow.run()

    def run_llmmig_workflow(self):
        round_name: RoundName = "llmmig"
        workflow = LLMMigWorkflow(self.project)
        project = self.project
        self.mig_log.log_event(f"Running {round_name}", "h2")
        project.git_reset()
        try:
            self._is_prerequisites_finished(round_name)
            mig_files = workflow.find_mig_locations()
            if mig_files:
                self.copy_to_premig(mig_files)
                workflow.run()
                project.apply_code_changes(round_name)
                self.validate(round_name)
            self.log_mig_result(mig_files, round_name, "premig")
        except MigError as e:
            self.log_error_result(e, round_name, "premig")
        finally:
            self.mig_log.log_event("llmmig finished", "l1")

    def _run_round_workflow(self, round_name: RoundName, workflow):
        project = self.project
        self.mig_log.log_event(f"Running {round_name}", "h2")
        project.git_reset()
        try:
            self._is_prerequisites_finished(round_name)
            mig_files = []
            if self._base_round_has_test_diff(round_name, workflow.base_round_name):
                mig_files = workflow.find_mig_locations()
                if mig_files:
                    self.copy_to_premig(mig_files)
                    workflow.run()
                    project.apply_code_changes(round_name)
                    self.validate(round_name)
            self.log_mig_result(mig_files, round_name, workflow.base_round_name)
        except MigError as e:
            self.log_error_result(e, round_name, workflow.base_round_name)
        finally:
            self.mig_log.log_event(f"{round_name} finished", "l1")

    def run_merge_workflow(self):
        workflow = SkippedCodeMergeWorkflow(self.project)
        self._run_round_workflow("merge_skipped", workflow)

    def run_async_workflow(self):
        workflow = InferredAsyncTransformWorkflow(self.project)
        self._run_round_workflow("async_transform", workflow)

    def run_manual_edit_workflow(self):
        round_name: RoundName = "manual_edit"
        workflow = ManualEditWorkflow(self.project)
        project = self.project
        self.mig_log.log_event(f"Running {round_name}", "h2")
        project.git_reset()
        workflow.run()
        project.apply_code_changes(round_name)
        self.validate(round_name)
        if workflow.mig_files:
            project.git_reset()
            self.copy_to_premig(workflow.mig_files)

        self.log_mig_result(workflow.mig_files, round_name, workflow.base_round_name)


    def validate(self, round_name: RoundName):
        paths = self.project.round_paths(round_name)
        if self.project.smart_skip_tests:
            if paths.utest_report.exists() and paths.cov_report.exists():
                self.mig_log.log_event("skipping tests", "l1")
                return

        self.project.run_tests(paths)

    def init_output(self):
        """
        Initialize the output directory for the mig.
        If directory is inside the project, is excluded from git via a .gitignore file.
        """
        self.project.output_path.mkdir(parents=True, exist_ok=True)
        if self.project.out_is_in_project:
            (self.project.output_path / ".gitignore").write_text("*\n")

    def log_mig_result(self, mig_files: list[str], this_round_name: RoundName, base_round_name: RoundName):
        log = self.mig_log
        project = self.project

        if not mig_files and not this_round_name == "manual_edit":
            # manual edit may have no files to migrate, bu tstill valid.
            # for example, we could not fix at all, or just installing a dependency fixed it
            round_report = MigRoundReport(
                name=this_round_name,
                base_round=base_round_name,
                status="finished - no files to migrate",
                project_change_coverage=0,
                files=[],
                test_diffs=[]
            )
            full_report = self.project.get_report()
            setattr(full_report, this_round_name, round_report)
            project.save_report()
            return

        premig_paths = project.premig_paths
        this_round_paths = project.round_paths(this_round_name)
        premig_report = premig_paths.read_utest_report()
        this_report = this_round_paths.read_utest_report()
        diff = UTestReportDiff(premig_report, this_report)

        if not diff.diffs:
            log.log_event("no test diff", "l1")

        log.log_event(f"test diff with round premig", "h3")
        for d in diff.diffs:
            log.log_event(f"`{d}`", "l1")

        cov_report = this_round_paths.read_cov_report()
        cov_files = cov_report["files"]

        report_files = []

        total_covered_lines = 0
        total_uncovered_lines = 0

        for file in mig_files:
            file_key = Path(file).as_posix()
            if file_key not in cov_files:
                report_file = MigRoundFileReport(file_key, 0, LineRange(), LineRange())
            # elif not premig_paths.code_file(file).exists():
            #     report_file = MigRoundFileReport(file_key, 0, LineRange(), LineRange())
            else:
                file_cov = cov_files[file_key]
                file_diff = compute_diff(premig_paths.read_code_file(file), this_round_paths.read_code_file(file))

                # todo, this is not entirely correct. because it does not consider removed lines
                changed_lines = set()
                for hunk in file_diff:
                    changed_lines.update(ln.target_line_no for ln in hunk.target_lines())
                covered_lines = set(file_cov["executed_lines"])

                covered_added_lines = changed_lines.intersection(covered_lines)
                uncovered_added_lines = changed_lines.difference(covered_lines)
                changed_coverage = safe_div(100 * len(covered_added_lines), len(changed_lines), 100)

                report_file = MigRoundFileReport(path=file_key,
                                                 file_change_coverage=changed_coverage,
                                                 covered_changed_lines=LineRange.from_values(covered_added_lines),
                                                 uncovered_changed_lines=LineRange.from_values(uncovered_added_lines))
                total_covered_lines += len(report_file.covered_changed_lines)
                total_uncovered_lines += len(report_file.uncovered_changed_lines)
            report_files.append(report_file)

        test_diffs = [td.as_report() for td in diff.diffs]
        project_change_coverage = safe_div(100 * total_covered_lines, total_covered_lines + total_uncovered_lines)

        round_report = MigRoundReport(
            name=this_round_name,
            base_round=base_round_name,
            status="finished",
            project_change_coverage=project_change_coverage,
            files=report_files,
            test_diffs=test_diffs
        )
        full_report = self.project.get_report()
        setattr(full_report, this_round_name, round_report)

        project.save_report()

    def log_error_result(self, e: MigError, this_round_name: RoundName, base_round_name: RoundName):
        round_report = MigRoundReport(
            name=this_round_name,
            base_round=base_round_name,
            status="error",
            error_code=e.error_code.value, error_type=e.error_type,
            error_message=e.message
        )
        full_report = self.project.get_report()
        setattr(full_report, this_round_name, round_report)
        self.project.save_report()
