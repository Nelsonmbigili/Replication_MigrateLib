import shutil
import sys

from git import Repo

from libmig_eval.util import Paths, Mig
from libmig_eval.util.models import decode_mig_id


def export_manual_edit(mig_id: str, base_round: str, force: bool = False):
    paths = Paths()
    mig_id = mig_id or input("migration id: ")
    base_round = base_round or input("base round: ")

    mig_props = decode_mig_id(mig_id)
    mig = Mig(mig_id, *mig_props)

    mig_out_dir = paths.mig_out_path(mig)
    manual_dir = mig_out_dir / f"{base_round}-manual" / "files"

    if manual_dir.exists() and not force:
        print(f"Manual edit already exists at {manual_dir}", file=sys.stderr)
        print("If you want to re-export, delete the existing directory", file=sys.stderr)
        return

    if manual_dir.exists():
        print(f"Deleting existing manual edit at {manual_dir}")
        shutil.rmtree(manual_dir)

    repo_path = paths.mig_repo_path(mig)

    git = Repo(repo_path)
    git_modified_files = {diff.a_path for diff in git.index.diff(None)}

    base_round_files_dir = mig_out_dir.joinpath(base_round, "files")
    base_round_files = {file.relative_to(base_round_files_dir).as_posix() for file in
                        base_round_files_dir.rglob("*.py")}

    added_files = git_modified_files - base_round_files
    reverted_files = base_round_files - git_modified_files
    remaining_files = git_modified_files & base_round_files

    modified_files = set()
    for file in remaining_files:
        current_version = (repo_path / file).read_text("utf-8")
        base_version = (base_round_files_dir / file).read_text("utf-8")
        if current_version != base_version:
            modified_files.add(file)

    for file in added_files | reverted_files | modified_files:
        print(f"Copying {file} from repo to manual edit")
        target = manual_dir.joinpath(file)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(repo_path.joinpath(file), target)


def main():
    mig_ids_str = """
alexferl@vyper__a0a6ea7f__toml__tomli
blingenf@copydetect__ba072818__jinja2__mako
blueprints-org@blueprints__b3bb6987__matplotlib__seaborn
k1m0ch1@bibit__9ae395ed__urllib3__pycurl
bormando@selenium-tools__52667925__urllib3__aiohttp
growthbook@growthbook-python__699fba51__aiohttp__requests
alpden550@encrypt-decrypt-fields__a0029320__sqlalchemy__tortoise-orm
avinassh@haxor__8c0cb6be__aiohttp__httpcore
cskorpion@vmprof-firefox-converter__e1f6bb79__flask__tornado
colour-science@colour-datasets__aa4ae7be__tqdm__alive-progress
fidelity@selective__7e07abc8__seaborn__altair
12932@cf-speedtest__78d9ee1d__requests__aiohttp
alinapetukhova@textcl__bff0bc18__torch__tensorflow
aboutcode-org@cwe2__e61804f9__importlib-resources__importlib_metadata
alpden550@encrypt-decrypt-fields__a0029320__cryptography__pycryptodome
aguinane@nem-reader__3558d00a__click__cliff
    """
    mig_ids = [mid.strip() for mid in mig_ids_str.strip().splitlines(keepends=False)]
    for mig_id in mig_ids:
        export_manual_edit(mig_id, "1", False)


if __name__ == "__main__":
    main()
