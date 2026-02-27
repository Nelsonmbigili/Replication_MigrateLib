from pathlib import Path

from libmig.mig.mig_report_models import load_report, RoundName
from libmig.project import create_round_path

from libmig_eval.config import MODEL_CODE
from libmig_eval.util.models import Mig


class Paths:
    def __init__(self):
        self.project_group_root = Path.cwd().parent

    def custom_req_file(self, mig: Mig):
        file = self.results_root / "custom_reqs" / f"{mig.repo_id}.requirements.txt"
        if file.exists():
            return file
        return None

    @property
    def libmig_project_root(self):
        return self.project_group_root / "LibMig"

    @property
    def eval_project_root(self):
        return Path.cwd()

    @property
    def repos_root(self):
        from libmig_eval.secrets import SECRETS
        configured = SECRETS.repo_root
        if configured:
            return Path(configured)
        return self.project_group_root / "repos"

    @property
    def venv_root(self):
        return self.project_group_root / "venvs"

    def repo_path(self, repo_id: str):
        return self.repos_root / repo_id

    def mig_repo_path(self, mig: Mig):
        return self.repos_root / mig.id

    def mig_venv_path(self, mig: Mig):
        # return self.venv_root / mig.id
        return self.mig_repo_path(mig) / ".venv"

    @property
    def paper_root(self):
        #return self.project_group_root / "LibMig-paper" # for paper
        return self.project_group_root / "../phd-thesis/tex/c5-tool"   # for thesis

    @property
    def seart_meta_list(self):
        return self.repo_db_root / "seart-meta-list.csv"

    @property
    def results_root(self):
        return self.project_group_root / "libmig-eval-results"

    @property
    def repo_db_root(self):
        return self.results_root / "repo_db"

    @property
    def mig_db_root(self):
        return self.results_root / "mig_db"

    @property
    def lib_db_root(self):
        return self.results_root / "lib_db"

    def mig_out_path(self, mig_or_mig_id: Mig | str, suffix=MODEL_CODE):
        id = mig_or_mig_id.id if isinstance(mig_or_mig_id, Mig) else mig_or_mig_id
        return self.results_root / f"libmig_out.{suffix}" / id

    def load_mig_report(self, mig: Mig):
        path = self.mig_out_path(mig) / "report.yaml"
        if not path.exists():
            return None
        return load_report(path)

    def load_test_report(self, mig: Mig, round_name: RoundName):
        return create_round_path(self.mig_out_path(mig), round_name).read_utest_report()
