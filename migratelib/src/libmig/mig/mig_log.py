import logging
from pathlib import Path

from libmig.mig.mig_error import MigError

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def format_line(line: str, format: str):
    if not format:
        return line
    code = format[0]

    if code == "h":
        level = int(format[1])
        return f"{'#' * level} {line}"
    if code == "l":
        level = 1 if len(format) == 1 else int(format[1])
        indent = level - 1
        return f"{'  ' * indent}- {line}"


class MigLog:
    def __init__(self, log_file: Path):
        if not log_file.exists():
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_file.touch()

        self.log_file = log_file

    def log_event(self, message: str, format: str = None):
        with open(self.log_file, "a") as f:
            message = format_line(message, format)
            f.write(f"{message}\n")
            logger.info(message)

    def log_list(self, items: list[str], format: str = "l1"):
        for item in items:
            self.log_event(item, format)

    def log_error(self, e: Exception):
        self.log_event(f"!! Error !!")
        if isinstance(e, MigError):
            self.log_list([
                f"Error code: {e.error_code}",
                f"Error type: {e.error_type}",
                f"Message: {e.message}",
            ], "l2")
        else:
            self.log_event(repr(e), "l1")
