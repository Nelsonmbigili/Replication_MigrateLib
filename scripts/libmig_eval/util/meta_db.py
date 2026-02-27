from collections import defaultdict
from pathlib import Path

import yaml


def _save_yaml(path: Path, data: dict):
    path.write_text(yaml.safe_dump(data, sort_keys=False), "utf-8")


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text("utf-8"))


class MetaDb:
    def __init__(self, db_root: Path):
        self.db_root = db_root

    def save(self, category: str, meta: dict):
        if path := self.find_meta_file(meta["id"]):
            print(f"Meta with id {meta['id']} already exists at {path}")
            return
        file = self._meta_file(category, meta["id"])
        file.parent.mkdir(parents=True, exist_ok=True)
        _save_yaml(file, meta)

    def load(self, category: str, item_id: str):
        return _load_yaml(self._meta_file(category, item_id))

    def find_and_load(self, item_id: str):
        file = self.find_meta_file(item_id)
        if file is None:
            return None
        return _load_yaml(file)

    def load_next(self, category: str):
        def try_load(attempt):
            try:
                file = next(self._meta_dir(category).glob("*.yaml"), None)
                if file is None:
                    return None
                return _load_yaml(file)
            except Exception as e:
                if attempt > 10:
                    raise e
                return try_load(attempt + 1)

        return try_load(0)

    def _meta_dir(self, category: str):
        return self.db_root / category

    def _meta_file(self, category: str, item_id: str):
        return self._meta_dir(category).joinpath(item_id + ".yaml")

    def find_meta_file(self, item_id: str):
        return next(self.db_root.rglob(f"{item_id}.yaml"), None)

    def has_meta(self, category: str, item_id: str):
        return self._meta_file(category, item_id).exists()

    def move(self, src_category: str, dst_category: str, item_id: str):
        try:
            src_file = self._meta_file(src_category, item_id)
            dst_file = self._meta_file(dst_category, item_id)
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            src_file.rename(dst_file)
            return True
        except FileNotFoundError:
            return False

    def all_ids(self, category: str):
        files = self._meta_dir(category).glob("*.yaml")
        return [f.stem for f in files]

    def export_category_stats(self):
        print("Exporting category stats")
        import pandas as pd
        all_files = self.db_root.rglob("*.yaml")
        data = []
        cat_summary = defaultdict(int)
        file: Path
        for file in all_files:
            category = file.parent.relative_to(self.db_root).as_posix()
            id = file.stem
            out = {"id": id, "category": category}
            data.append(out)
            cat_summary[category] += 1
        df = pd.DataFrame(data)
        csv_file = self.db_root / f"category_stats.csv"
        df.to_csv(csv_file, index=False)
        print(f"Exported category stats to {csv_file.as_posix()}")
        print("Category summary:")
        for cat, count in cat_summary.items():
            print(f"  {cat}: {count}")

    def count(self, category: str):
        return len(list(self._meta_dir(category).rglob("*.yaml")))

    def count_all(self):
        return len(list(self.db_root.rglob("*.yaml")))

    def all_categories(self):
        d: Path
        for d in self.db_root.rglob("*"):
            if d.is_dir():
                yield d.relative_to(self.db_root).as_posix()
