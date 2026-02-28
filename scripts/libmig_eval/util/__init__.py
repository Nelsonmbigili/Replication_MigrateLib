import os
import shutil
import stat
from pathlib import Path

from libmig.project import Project

from libmig_eval.config import MODEL_NAME
from libmig_eval.util.models import Mig
from libmig_eval.util.paths import Paths


def delete_dir(path: Path):
    def on_rm_error(func, sub_path, exc_info):
        if os.path.isfile(sub_path):
            # sometimes the file is read-only, so make it writeable
            os.chmod(sub_path, stat.S_IWRITE)
            try:
                os.unlink(sub_path)
            except:
                pass

    if path.exists():
        try:
            shutil.rmtree(path, onerror=on_rm_error)
        except:
            pass


def create_project(mig: Mig, rounds: set[str], dry_run: bool = False, use_cache=True,
                   smart_skip_tests=False) -> Project:
    p = Paths()

    from libmig_eval.secrets import SECRETS
    code_path = p.mig_repo_path(mig)
    req_files = [code_path / "requirements.txt"]
    custom_req_file = p.custom_req_file(mig)
    python_version = "3.14"
    if custom_req_file:
        req_files.append(custom_req_file)
        req_lines = custom_req_file.read_text(encoding="utf-8").splitlines()
        if req_lines and req_lines[0].startswith("# python"):
            python_version = req_lines[0].split("==")[1].strip()

    return Project(
        source=mig.source,
        target=mig.target,
        code_path=code_path,
        requirements_file_paths=req_files,
        rounds=rounds,
        smart_skip_tests=smart_skip_tests,
        use_cache=use_cache,
        force_rerun=True,
        llm=MODEL_NAME,
        dry_run=dry_run,
        output_path=p.mig_out_path(mig),
        openai_api_key=SECRETS.openai_api_key,
        python_version=python_version,
    )
