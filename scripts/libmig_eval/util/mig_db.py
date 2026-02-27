from pathlib import Path

import pandas as pd

from libmig_eval.util.meta_db import MetaDb
from libmig_eval.util.models import Mig


class MigDb:
    def __init__(self, db_path: Path):
        inner = MetaDb(db_path)
        all_ids = inner.all_ids("included")
        self._migs = [Mig(**inner.load("included", id)) for id in all_ids]
        self._mig_index = {mig.id: mig for mig in self._migs}

    def all_migs(self):
        return self._migs

    def get_mig(self, mig_id: str):
        return self._mig_index.get(mig_id)
