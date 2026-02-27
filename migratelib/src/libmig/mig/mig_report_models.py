from pathlib import Path
from typing import Literal

import yaml
from dataclasses import dataclass

from libmig.utils.line_range import LineRange

RoundName = Literal["premig", "llmmig", "merge_skipped", "async_transform", "manual_edit"]
AllMigRoundNames: list[RoundName] = ["llmmig", "merge_skipped", "async_transform"]
AllRoundNames: list[RoundName] = ["premig", *AllMigRoundNames, "manual_edit"]


def encode_mig_id(repo: str, commit: str, src: str, tgt: str) -> str:
    commit = commit[:8]
    repo = repo.replace("/", "@")
    return f"{repo}__{commit}__{src}__{tgt}"


@dataclass
class PremigRoundReport:
    name: Literal["premig"]
    status: Literal["finished", "error"]
    source_version: str | None = None
    target_version: str | None = None
    finished_at: str | None = None
    project_coverage: float | None = None
    total_tests: int | None = None
    passed_tests: int | None = None

    error_code: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    error_traceback: str | None = None

    def is_finished(self):
        return self.status in {"finished"}

    def has_results(self):
        return bool(self.status == "finished" and self.total_tests and self.passed_tests)

    def to_dict(self):
        raw = dict(self.__dict__)

        if self.status != "error":
            raw.pop("error_code", None)
            raw.pop("error_type", None)
            raw.pop("error_message", None)
            raw.pop("error_traceback", None)

        return raw

    @classmethod
    def from_dict(cls, raw: dict):
        return cls(**raw)


@dataclass
class MigRoundFileReport:
    path: str
    file_change_coverage: float
    covered_changed_lines: LineRange = None
    uncovered_changed_lines: LineRange = None

    def to_dict(self):
        return {
            "path": self.path,
            "file_change_coverage": self.file_change_coverage,
            "covered_changed_lines": self.covered_changed_lines.expression,
            "uncovered_changed_lines": self.uncovered_changed_lines.expression,
        }

    @classmethod
    def from_dict(cls, raw: dict):
        raw["covered_changed_lines"] = LineRange(raw["covered_changed_lines"])
        raw["uncovered_changed_lines"] = LineRange(raw["uncovered_changed_lines"])
        return cls(**raw)


@dataclass
class UTestDiffReport:
    test_id: str
    before: str
    after: str
    failed_phase: Literal["collection", "setup", "call", "teardown"]
    exception: str
    error_message: str

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, raw: dict):
        return cls(**raw)


@dataclass
class MigRoundReport:
    name: RoundName

    base_round: RoundName
    """The round on which the migration is applied"""

    status: Literal["finished", "error", "finished - no files to migrate"]
    project_change_coverage: float | None = None
    files: list[MigRoundFileReport] = None
    test_diffs: list[UTestDiffReport] = None

    error_code: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    error_traceback: str | None = None

    def is_finished(self):
        """
        Whether the round is finished or not. This is useful to check whether the round needs to be retried.
        :return:
        """
        return self.status in {"finished", "finished - no files to migrate"}

    def has_results(self):
        """
        Check if the round has results. This is different from is_finished, because a round may be successfully
        finished, but may not have any results to report.
        :return:
        """
        return bool(self.status == "finished")

    def to_dict(self):
        raw = dict(self.__dict__)
        if self.files is not None:
            raw["files"] = [file.to_dict() for file in self.files]
        if self.test_diffs is not None:
            raw["test_diffs"] = [diff.to_dict() for diff in self.test_diffs]

        if self.status != "error":
            raw.pop("error_code", None)
            raw.pop("error_type", None)
            raw.pop("error_message", None)
            raw.pop("error_traceback", None)

        return raw

    @classmethod
    def from_dict(cls, raw: dict):
        if "files" in raw and raw["files"]:
            files = [MigRoundFileReport.from_dict(raw_file) for raw_file in raw["files"]]
            raw["files"] = files
        if "test_diffs" in raw and raw["test_diffs"]:
            test_diffs = [UTestDiffReport.from_dict(raw_diff) for raw_diff in raw["test_diffs"]]
            raw["test_diffs"] = test_diffs
        return cls(**raw)


@dataclass
class MigReport:
    mig: str
    repo: str
    commit: str
    source: str
    target: str
    premig: PremigRoundReport = None
    llmmig: MigRoundReport = None
    merge_skipped: MigRoundReport = None
    async_transform: MigRoundReport = None
    manual_edit: MigRoundReport = None

    def to_dict(self):
        raw = dict(self.__dict__)

        for round_name in AllRoundNames:
            round_report = self.get_round_report(round_name)
            if round_report:
                raw[round_name] = round_report.to_dict()

        return raw

    @classmethod
    def from_dict(cls, raw: dict):
        for round_name in AllRoundNames:
            if round_name in raw and raw[round_name]:
                if round_name == "premig":
                    raw[round_name] = PremigRoundReport.from_dict(raw[round_name])
                else:
                    raw[round_name] = MigRoundReport.from_dict(raw[round_name])

        return cls(**raw)

    def get_round_report(self, round_name: RoundName) -> PremigRoundReport | MigRoundReport:
        if round_name not in AllRoundNames:
            raise ValueError(f"Invalid round name {round_name}")

        round_report = getattr(self, round_name)
        return round_report

    def get_best_round(self, rounds: list[RoundName] = None, prefer_later_when_equal: bool = False):
        if rounds is None:
            rounds = AllMigRoundNames

        best_test_diffs = 10000000  # just a large number. Noone has so many tests
        best_round_name = None
        for round_name in rounds:
            round_report = self.get_round_report(round_name)
            if round_report is None:
                continue
            if not round_report.has_results():
                continue
            diffs = len(round_report.test_diffs)
            if diffs < best_test_diffs:
                best_test_diffs = diffs
                best_round_name = round_name
            elif diffs == best_test_diffs and prefer_later_when_equal:
                # For example, LLMMig and Merge Skipped are both run, and Merge Skipped did not make the tests better or
                # worse. If prefer_later_when_equal is True, we will prefer Merge Skipped. If false, we will keep
                # LLMMig.
                best_round_name = round_name

        return best_round_name


def load_report(file_path: Path) -> MigReport:
    content = file_path.read_text("utf-8")
    raw = yaml.safe_load(content)
    report = MigReport.from_dict(raw)
    return report


def save_report(file_path: Path, report: MigReport):
    raw = report.to_dict()
    content = yaml.safe_dump(raw, sort_keys=False)
    file_path.write_text(content, "utf-8")
