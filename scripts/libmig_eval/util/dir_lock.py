import json
from datetime import datetime, timedelta
from pathlib import Path


class DirLock:
    def __init__(self, path: Path, create_dir_if_not_exists: bool = True):
        self.path = path
        self.create_dir_if_not_exists = create_dir_if_not_exists
        self._lockfile = path / '.lock'

    def _force_acquire(self, minutes: float):
        expires = datetime.now() + timedelta(minutes=minutes)
        if not self._lockfile.parent.exists() and self.create_dir_if_not_exists:
            self._lockfile.parent.mkdir(parents=True)
        self._lockfile.write_text(json.dumps({
            "expires": expires.isoformat()
        }), "utf-8")

    def try_acquire(self, minutes: float):
        if self._lockfile.exists():
            content = self._lockfile.read_text("utf-8")
            obj = json.loads(content)
            time = datetime.fromisoformat(obj["expires"])
            now = datetime.now()
            if now < time:
                return False

        self._force_acquire(minutes)
        return True

    def release(self):
        if self._lockfile.exists():
            self._lockfile.unlink()
