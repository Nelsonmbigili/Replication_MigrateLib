import shutil
from pathlib import Path

from libmig.cmd import run
from libmig.mig.mig_report_models import RoundName, AllRoundNames
from libmig.mig.mig_round_paths import MigRoundPaths, create_round_path


class ProjectGit:
    def __init__(self, code_path: Path):
        self.code_path = code_path

    def reset(self):
        run(["git", "reset", "--hard"], cwd=self.code_path)

    def apply_code_changes(self, output_path: Path, round_name: RoundName):
        """
        Update the project with the migrated code.
        Note that the second and later level migrations does not necessarily migrate all files.
        Therefore, a previous level migration would apply in this case.
        Also note that we clean the project before migration round.
        So, when updating the code, we start applying from round 1, and keep going forward to later rounds.
        :return:
        """

        self.reset()
        applied_files = set()
        for rn in AllRoundNames:
            round_paths = create_round_path(output_path, rn)
            for file in round_paths.mig_code_files:
                applied_files.add(file)
                shutil.copy2(round_paths.code_file(file), self.file_path(file))

            if round_name == rn:
                break

        return applied_files

    def file_path(self, relative_path: str):
        """ Get the absolute path of a file in the project directory."""
        return self.code_path / relative_path
