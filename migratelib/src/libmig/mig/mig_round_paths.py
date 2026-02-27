import json
import shutil
from pathlib import Path

from libmig.mig.mig_report_models import AllRoundNames
from libmig.utest import UTestReport


def create_round_path(mig_out_path: Path, round_name, base: 'MigRoundPaths' = None) -> 'MigRoundPaths':
    index = AllRoundNames.index(round_name)
    round_path = mig_out_path / f"{index}-{round_name}"
    return MigRoundPaths(round_path, base=base)


class MigRoundPaths:
    def __init__(self, round_path: Path, base: 'MigRoundPaths' = None):
        self.round_path = round_path
        self.base = base

    @property
    def profile_report(self):
        return self.round_path / "profile.callgrind"

    @property
    def utest_report(self):
        return self.round_path / "test-report.json"

    def read_utest_report(self):
        return UTestReport.load_from_file(self.utest_report)

    @property
    def cov_report(self):
        return self.round_path / "cov-report.json"

    @property
    def cg(self):
        return self.round_path / "cg.yaml"

    def read_cov_report(self):
        return json.loads(self.cov_report.read_text())

    @property
    def files_root(self):
        return self.round_path / "files"

    @property
    def mig_code_files(self) -> list[str]:
        """The files that were migrated in this round. This gives the list by traversing the results directory.
        Therefore, only available after the migration is finished."""
        return [f.relative_to(self.files_root).as_posix() for f in self.files_root.glob("**/*.py")]

    def code_file(self, file_relative_path: str | Path):
        return self.file_with_suffix(file_relative_path, ".py")

    def read_code_file(self, file_relative_path: str | Path):
        """Read the content of a code file. If the file is not found, read from base round recursively if available."""
        code_file = self.code_file(file_relative_path)
        if not code_file.exists():
            if self.base:
                return self.base.read_code_file(file_relative_path)
            raise FileNotFoundError(f"Code file {code_file} not found in round {self.round_path}")
        return code_file.read_text("utf-8")

    def write_code_file(self, file_relative_path: str | Path, content: str):
        path = self.code_file(file_relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, "utf-8")

    def file_with_suffix(self, file_relative_path: str | Path, suffix: str, create_dirs: bool = False):
        file_path = self.file(file_relative_path).with_suffix(suffix)
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path

    def file(self, file_relative_path: str | Path):
        """Get the file path without suffix."""
        return self.files_root / file_relative_path

    def copy_file(self, file: str, abs_path: Path):
        """Copy a file to the round's files directory ONLY IF IT DOESN'T EXIST."""
        target_path = self.files_root / file
        if target_path.exists():
            import sys
            print(f"File {target_path} already exists, skipping copy.", file=sys.stderr)
            return
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(abs_path, target_path)
