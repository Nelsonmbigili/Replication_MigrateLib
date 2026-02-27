import pandas as pd

from libmig_eval.util import delete_dir
from libmig_eval.util.models import Mig
from libmig_eval.util.paths import Paths
from libmig_eval.util.run_cmd import shallow_clone, run_cmd, pip_install

__custom_reqs = {}


def get_custom_reqs(repo: str):
    global __custom_reqs
    if not __custom_reqs:
        __custom_reqs = pd.read_csv("data/custom_requirements.csv")

    return __custom_reqs[__custom_reqs["repo"] == repo]["requirement"]


def prepare_mig_repo(mig: Mig):
    paths = Paths()
    repo_path = paths.mig_repo_path(mig)
    if not repo_path.exists():
        print(f" Cloning {mig.repo_id} to {repo_path.as_posix()}")
        shallow_clone(mig.repo, mig.commit, repo_path)

    return repo_path


def cleanup_mig_repo(mig: Mig):
    paths = Paths()
    print(f" Cleaning up {mig.id}")
    delete_dir(paths.mig_repo_path(mig))
    delete_dir(paths.mig_venv_path(mig))
