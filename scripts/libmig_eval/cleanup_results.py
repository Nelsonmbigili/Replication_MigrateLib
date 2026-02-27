import shutil

import yaml

from libmig_eval.mig_runner import sample_migs
from libmig_eval.util.paths import Paths


def main():
    if input("CAUTION. This will cleanup all results in mig_out_path. Press enter 'y' to continue.") != "y":
        print("Aborted. Good for you.")
        return
    paths = Paths()
    from libmig_eval.util.mig_db import MigDb
    mig_db = MigDb(paths.mig_db_root)
    migs = mig_db.all_migs()
    migs = sample_migs(migs)

    for mig in migs:
        print(mig.id)
        current_out_path = paths.mig_out_path(mig, "4omini")
        clean_out_path = paths.mig_out_path(mig, "4omini-clean")
        if clean_out_path.exists():
            shutil.rmtree(clean_out_path)

        shutil.copytree(current_out_path, clean_out_path)

        manual_path = clean_out_path.joinpath("1-manual")
        r2_path = clean_out_path.joinpath("2")

        if manual_path.exists():
            shutil.rmtree(manual_path)
        if r2_path.exists():
            shutil.rmtree(r2_path)

        premig_path = clean_out_path.joinpath("0")
        premig_path.rename(clean_out_path.joinpath("0-premig"))

        llmmig_path = clean_out_path.joinpath("1")
        llmmig_path.rename(clean_out_path.joinpath("1-llmmig"))

        report = yaml.unsafe_load(clean_out_path.joinpath("report.yaml").open())
        rounds = report["rounds"]
        report.pop("rounds", None)

        report["premig"] = {"name": "premig"}
        report["premig"].update(rounds[0])

        if rounds[1]:
            report["llmmig"] = {"name": "llmmig"}
            report["llmmig"].update(rounds[1])

        clean_out_path.joinpath("report.yaml").write_text(yaml.safe_dump(report))


if __name__ == '__main__':
    main()
