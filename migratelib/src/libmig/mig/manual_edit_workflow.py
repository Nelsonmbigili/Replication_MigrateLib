import time
from pathlib import Path
from subprocess import Popen

from git import Repo

from libmig.project import Project


class ManualEditWorkflow:
    def __init__(self, project: Project):
        self.project = project
        self.mig_files = []
        self.log = self.project.get_loger()
        self._fix_description_file = self.project.git.file_path("fix.md")

    @property
    def base_round_name(self):
        if not hasattr(self, "_base_round_name_instance"):
            self._base_round_name_instance = self._report.get_best_round(prefer_later_when_equal=True) or "llmmig"
        return self._base_round_name_instance

    def open_editor(self):
        self.log.log_event("Opening editor for manual edits", "l1")
        process = Popen(["pycharm64", self.project.code_path])
        process.wait()

        # I could not find a way to wait for the editor to be closed, so I am using a prompt in the command line here.
        if input("Press x to discard edits. Press any other key to finish editing: ") == "x":
            self.log.log_event("Discarding edits", "l1")
            return False

        self.log.log_event("Finished editing", "l1")
        return True

    @property
    def _report(self):
        if not hasattr(self, "_report_instance"):
            self._report_instance = self.project.get_report()
        return self._report_instance

    def run(self):
        self.project.apply_code_changes(self.base_round_name)
        self.prepare()
        if self.open_editor():
            self.process_edits()

    def prepare(self):
        premig_ut = self.project.premig_paths.read_utest_report()
        base_ut = self.project.round_paths(self.base_round_name).read_utest_report()

        self.log.log_event(f"Premig round: {premig_ut.summary.passed}/{premig_ut.summary.total} passed", "l1")
        self.log.log_event(f"Base round ({self.base_round_name}): {base_ut.summary.passed} passed", "l1")
        while not self._fix_description_file.exists():
            self._fix_description_file.touch()

    def process_edits(self):

        git = Repo(self.project.code_path)
        diffs = git.index.diff(None)
        base_round_paths = self.project.round_paths(self.base_round_name)

        for diff in diffs:
            rel_path = Path(diff.a_path).as_posix()
            project_path = self.project.git.file_path(rel_path)
            base_round_path = base_round_paths.file(rel_path)
            if base_round_path.exists():
                base_round_content = base_round_path.read_text("utf-8")
                current_content = project_path.read_text("utf-8")
                if base_round_content == current_content:
                    continue

            self.mig_files.append(rel_path)
            self.project.manual_edit_paths.copy_file(rel_path, project_path)

        input("Press any key if you after you edit the fix description file: ")

        fix_description_file = self._fix_description_file
        fix_description_copy = self.project.manual_edit_paths.round_path / "fix.md"
        fix_description_copy.unlink(missing_ok=True)
        fix_description_copy.parent.mkdir(parents=True, exist_ok=True)
        fix_description_file.rename(fix_description_copy)
