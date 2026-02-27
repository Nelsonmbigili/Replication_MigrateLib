from os import PathLike
from pathlib import Path

from platformdirs import user_cache_dir

_cache_dir = Path(user_cache_dir("libmig"))


def read_cache(relative_path: PathLike | str, format: str = None):
    """
    Read a file from the cache directory.
    :param relative_path:
    :param format: The following formats are supported:
        - None - determine the format from the file extension
        - "text" - read the file as text
        - "csv" - read the file as a CSV file, return a pandas DataFrame
        - "json" - read the file as a JSON file, return a dict
    :return:
    """
    full_path = cache_file_path(relative_path)
    if not full_path.exists():
        return None

    if not format:
        format = full_path.suffix[1:].lower()

    if format in {"text", "txt"}:
        return full_path.read_text("utf-8")
    if format == "csv":
        import pandas as pd
        return pd.read_csv(full_path)
    if format == "json":
        import json
        return json.load(full_path.open("r"))

    raise ValueError(f"Unsupported format {format}")


def write_cache(relative_path: PathLike | str, content: any, format: str = None):
    full_path = cache_file_path(relative_path)
    if not format:
        format = full_path.suffix[1:].lower()

    if format in {"text", "txt"}:
        text_content = content or ""
    elif format == "csv":
        text_content = content.to_csv(index=False)
    elif format == "json":
        import json
        text_content = json.dumps(content, indent=2)
    else:
        raise ValueError(f"Unsupported format {format}")

    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(text_content, "utf-8")


def cache_file_path(relative_path: str):
    return _cache_dir / relative_path


def has_cache(relative_path: PathLike | str):
    return cache_file_path(relative_path).exists()
