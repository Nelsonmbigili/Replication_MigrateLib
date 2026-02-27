from pathlib import Path

import yaml

from libmig_eval.latex.utils import to_macro_name, try_format_int


def _build_new_command_macro(key: str, value: any):
    return "\\newcommand{" + key + "}{" + str(value) + "\\xspace}"


def percent(numerator, denominator=1, escape_latex=True):
    if denominator == 0:
        return "-"
    p = 100 * numerator / denominator
    return format_percent(p, escape_latex=escape_latex)


def format_percent(value, decimals=None, escape_latex=True):
    if decimals is None:
        decimals = 1 if value < 9.5 else 0
    # decimals = 1
    percent_sign = "\\%" if escape_latex else "%"
    return ("{0:." + str(decimals) + "f}").format(value) + percent_sign


def format_float(value, decimals=2):
    return ("{0:." + str(decimals) + "f}").format(value)


class LatexResultData:
    """Store and update data for the paper"""

    def __init__(self, paper_root: Path):
        self.yaml_path = (paper_root / "meta" / "results.yaml").resolve().absolute()
        self.tex_path = (paper_root / "meta" / "results.tex").resolve().absolute()
        self.yaml_path.touch(exist_ok=True)
        self.tex_path.touch(exist_ok=True)
        self._data: dict = yaml.safe_load(self.yaml_path.read_text("utf8")) or {}

    def update(self, new_data: dict[str, any]):
        new_data = {to_macro_name(k): try_format_int(v) for k, v in new_data.items()}
        self._data.update(new_data)
        self._data = {k: self._data[k] for k in sorted(self._data)}
        print("writing to " + str(self.yaml_path))
        self.yaml_path.write_text(yaml.safe_dump(self._data, sort_keys=False) + "\n", "utf8")

        all_defs = "\n".join(_build_new_command_macro(key, value) for key, value in self._data.items())
        print("writing to " + str(self.tex_path))
        self.tex_path.write_text(all_defs + "\n", encoding="utf8")

    def clean(self):
        self.yaml_path.write_text("", "utf8")
        self.tex_path.write_text("", "utf8")
        self._data = {}
