import inspect
from dataclasses import dataclass, fields
from os import PathLike
from pathlib import Path

from libmig.code_analysis.cg import function_id


class _DefaultLoad:
    def __init__(self, **kwargs):
        pass

    @classmethod
    def load(cls, data: dict):
        params = inspect.signature(cls).parameters
        return cls(**{k: v for k, v in data.items() if k in params})


@dataclass
class UTestSummary:
    """TestSummary class"""

    total: int
    collected: int
    passed: int = 0
    skipped: int = 0
    failed: int = 0
    error: int = 0
    xfailed: int = 0
    xpassed: int = 0


@dataclass
class UTestCollector(_DefaultLoad):
    """TestCollector class"""

    nodeid: str
    outcome: str
    result: list[dict]


@dataclass
class TracebackItem(_DefaultLoad):
    path: str
    lineno: int
    message: str


@dataclass
class Crash(_DefaultLoad):
    path: str | Path
    lineno: int
    message: str


@dataclass
class UTestItemResult(_DefaultLoad):
    outcome: str
    crash: Crash = None
    traceback: list[TracebackItem] = None
    longrepr: str = None

    def __post_init__(self):
        if self.traceback is not None:
            self.traceback = [TracebackItem.load(tb) for tb in self.__dict__["traceback"]]
        if self.crash is not None:
            self.crash = Crash.load(self.__dict__["crash"])
        self.failed = self.outcome == "failed"
        self.passed = self.outcome == "passed"
        self.skipped = self.outcome == "skipped"


@dataclass
class UTestItem:
    nodeid: str
    lineno: int
    """
    This line number is not the exact line number of the test function.
    There are two things we know of. The line number seem to start from 0.
    Then if there are any annotations, the line number considers the annotations as well.
    Overall, this is not reliable in correctly identifying the function location.
    """
    outcome: str
    keywords: list[str]
    setup: UTestItemResult
    teardown: UTestItemResult = None
    call: UTestItemResult = None

    @classmethod
    def load(cls, data: dict):
        """Load data into UTestItem"""
        data["setup"] = UTestItemResult.load(data["setup"])
        if "call" in data:
            data["call"] = UTestItemResult.load(data["call"])
        if "teardown" in data:
            data["teardown"] = UTestItemResult.load(data["teardown"])
        return cls(**data)

    def __post_init__(self):
        id_parts = self.nodeid.split("::")
        file, name = id_parts[0], id_parts[-1]
        self.filepath = file
        self.function_name = name

        self.failed = self.outcome == "failed"
        self.passed = self.outcome == "passed"
        self.skipped = self.outcome == "skipped"
        self.phases = [self.setup, self.call, self.teardown]

        self.failed_phase: UTestItemResult | None = None
        self.failed_phase_name = None
        for phase_name in ["setup", "call", "teardown"]:
            phase = getattr(self, phase_name)
            if phase is None:
                continue
            if phase.outcome == "failed":
                self.failed_phase = phase
                self.failed_phase_name = phase_name
                break

        if self.failed_phase:
            self.error_type = self.failed_phase.traceback[-1].message if self.failed_phase.traceback else "unknown"

    def __hash__(self):
        return hash(self.nodeid)

    def __eq__(self, other):
        return self.nodeid == other.nodeid

    def __ne__(self, other):
        return not self.__eq__(other)


@dataclass
class UTestWarning:
    """TestWarning class"""

    message: str
    category: str
    when: str
    filename: str
    lineno: int


@dataclass
class UTestReport:
    """TestReport class"""

    exitcode: int
    summary: UTestSummary
    collectors: list[UTestCollector]
    tests: list[UTestItem]
    warnings: list[UTestWarning]

    def __post_init__(self):
        self.has_tests = self.summary.collected > 0
        self.has_running_tests = self.summary.total > 0

    @classmethod
    def load(cls, data: dict):
        """Load data into UTestReport"""
        formatted_data = {
            "summary": UTestSummary(**data["summary"]),
            "collectors": [UTestCollector.load(col) for col in data["collectors"]],
            "tests": [UTestItem.load(test) for test in data["tests"]],
            "warnings": [UTestWarning(**warn) for warn in data.get("warnings", [])],
            "exitcode": data["exitcode"],
        }

        return cls(**formatted_data)

    @classmethod
    def load_from_file(cls, filepath: PathLike):
        """Load UTestReport from file"""
        import json
        data = json.load(open(filepath))
        return cls.load(data)

    def failed_tests(self):
        """Get failed tests"""
        return [test for test in self.tests if test.failed]

    def passed_tests(self):
        """Get passed tests"""
        return [test for test in self.tests if test.passed]
