import json
import shutil
from pathlib import Path

import yaml

from libmig.cmd import run, run_and_get_output
from libmig.lib_index.lib_index import LibIndex
from libmig.llm_clients import OpenAIClient
from libmig.mig.mig_error import MigError, ErrorCode
from libmig.mig.mig_log import MigLog
from libmig.mig.mig_report_models import MigReport, save_report, load_report, RoundName, AllRoundNames, encode_mig_id
from libmig.mig.mig_round_paths import MigRoundPaths, create_round_path
from libmig.project_git import ProjectGit
from libmig.utils.venv import get_venv


def _default_if_none(val, default):
    return default if val is None else val


class Project:
    # Todo: gradually refactor this class to make it a factory class for different services.
    # This class itself should not have any other logic.
    def __init__(self,
                 source: str,
                 target: str,
                 code_path: Path,
                 openai_api_key: str = None,
                 rounds: set[str] = None,
                 llm: str = None,
                 requirements_file_paths: list[Path] = None,
                 test_root: Path = None,
                 output_path: Path = None,
                 use_cache: bool = None,
                 force_rerun: bool = False,
                 max_files: int = None,
                 smart_skip_tests: bool = None,
                 dry_run: bool = False,
                 repo: str = None,
                 python_version: str = None,
                 ):
        self.openai_api_key = openai_api_key
        self.dry_run = dry_run
        rounds = rounds or set()
        if not test_root:
            test_root = code_path
        if not requirements_file_paths:
            requirements_file_paths = [code_path / "requirements.txt"]

        if not output_path:
            output_path = code_path / f".libmig/{source}__{target}"

        if not repo:
            repo = code_path.name

        commit = run_and_get_output(["git", "rev-parse", "HEAD"], cwd=code_path).strip()

        use_cache = _default_if_none(use_cache, True)
        max_files = _default_if_none(max_files, 20)
        smart_skip_tests = _default_if_none(smart_skip_tests, False)

        llm = _default_if_none(llm, "openai gpt-4o-mini")
        python_version = _default_if_none(python_version, "3.12")

        self.source = source
        self.target = target
        self.code_path = code_path
        self.test_root = test_root
        self.use_cache = use_cache
        self.force_rerun = force_rerun
        self.max_files = max_files
        self.smart_skip_tests = smart_skip_tests
        self.output_path = output_path
        self.llm = llm
        self.rounds = rounds
        self.requirements_file_paths = requirements_file_paths
        self.venv_path = code_path / ".venv"
        self.repo = repo
        self.commit = commit
        self.python_version = python_version

        self.venv = get_venv(self.venv_path, self.python_version)
        self.git = ProjectGit(code_path)
        self._lib_indexes = {}

        assert code_path.exists(), f"code path {code_path} does not exist"
        assert test_root.exists(), f"test root {test_root} does not exist"
        for req_file in requirements_file_paths:
            assert req_file.exists(), f"requirements file {req_file} does not exist"

        self._round_paths = {}
        self._source_lib_paths = None
        self._report_instance = None

    def _get_lib_index(self, lib_name: str) -> LibIndex:
        if lib_name not in self._lib_indexes:
            self._lib_indexes[lib_name] = LibIndex.from_venv(lib_name, self.venv)
        return self._lib_indexes[lib_name]

    @property
    def source_lib(self):
        return self._get_lib_index(self.source)

    @property
    def target_lib(self):
        return self._get_lib_index(self.target)

    @property
    def _report_path(self):
        return self.output_path / "report.yaml"

    @property
    def source_lib_paths(self):
        if self._source_lib_paths is None:
            self._source_lib_paths = [self.venv.lib_path(imn) for imn in self.source_lib.import_names]

        assert self._source_lib_paths, f"source lib path not found for {self.source}"
        return self._source_lib_paths

    def get_loger(self):
        return MigLog(self.output_path / "log.md")

    def file_path(self, relative_path: str):
        return self.code_path / relative_path

    @property
    def out_is_in_project(self):
        return self.output_path.is_relative_to(self.code_path)

    def is_client_code(self, file: Path):
        return file.is_relative_to(self.code_path) and not file.is_relative_to(self.venv_path)

    def path_in_source_lib(self, file: Path):
        for lib_path in self.source_lib_paths:
            if file.is_relative_to(lib_path):
                return file.relative_to(lib_path.parent)

        return None

    def path_in_project(self, file: Path):
        if file.is_relative_to(self.code_path):
            return file.relative_to(self.code_path)

        return None

    def run_tests(self, paths: MigRoundPaths, cov_all_files=False):
        log = self.get_loger()
        log.log_event(f"running tests", "h3")
        json_file = paths.utest_report
        xml_file = json_file.with_suffix(".xml")
        html_file = json_file.with_suffix(".html")
        cov_file = paths.cov_report

        for file in [json_file, xml_file, html_file, cov_file]:
            file.unlink(missing_ok=True)

        test_args = [
            "--durations-min=5.0",  # show duration for tests that take more than 5 seconds
            "--rootdir", self.test_root.as_posix(), "--cache-clear",
            "--junitxml", xml_file,
            "--html", html_file,
            "--cov",
            "--json-report",
            "--json-report-file", json_file, "--json-report-indent", "2",
        ]

        utest_status = self.venv.run_script("python", "-m", "pytest", *test_args, cwd=self.code_path, read_output=False)

        cov_args = ["json", "-o", cov_file]
        if not cov_all_files:
            cov_args += ["--include", ",".join(paths.mig_code_files)]
        cov_status = self.venv.run_script("coverage", *cov_args, cwd=self.code_path, read_output=False)

        if not json_file.exists():
            _save_empty_test_report(utest_status, json_file)
        if not cov_file.exists():
            _save_empty_cov_report(cov_file)

        def format_duration(d: dict):
            d.pop("duration", None)
            d.pop("created", None)
            d.pop("environment", None)
            d.pop("root", None)
            d.pop("log", None)
            return d

        test_report = json.loads(json_file.read_text(), object_hook=format_duration)
        json_file.write_text(json.dumps(test_report, indent=2))
        json_file.with_suffix(".yaml").write_text(yaml.dump(test_report))

        cov_report = json.loads(cov_file.read_text())
        cov_file.write_text(_format_cov_report(cov_report))

        log.log_event(f"test finished with status {utest_status}, cov finished with status {cov_status}", "l1")

    def git_reset(self):
        run(["git", "reset", "--hard"], cwd=self.code_path)

    def save_report(self):
        save_report(self._report_path, self.get_report())

    def get_report(self):
        if not self._report_instance:
            if self._report_path.exists():
                self._report_instance = load_report(self._report_path)
            else:
                mig_id = encode_mig_id(self.repo, self.commit, self.source, self.target)
                self._report_instance = MigReport(mig_id, self.repo, self.commit, self.source, self.target)

        return self._report_instance

    @property
    def premig_paths(self):
        return self.round_paths("premig")

    @property
    def llmmig_paths(self):
        return self.round_paths("llmmig")

    @property
    def merge_paths(self):
        return self.round_paths("merge_skipped")

    @property
    def async_paths(self):
        return self.round_paths("async_transform")

    @property
    def manual_edit_paths(self):
        return self.round_paths("manual_edit")

    def round_paths(self, round_name: RoundName) -> MigRoundPaths:
        if round_name not in self._round_paths:
            self._round_paths[round_name] = create_round_path(self.output_path, round_name)

        return self._round_paths[round_name]

    def create_llm_client(self):
        if self.llm.startswith("gpt-"):
            return OpenAIClient(self.openai_api_key, self.llm)

        raise MigError(ErrorCode.LLM_UNKNOWN_CLIENT, "unknown client", f"Unknown client: {self.llm}")

    def apply_code_changes(self, round_name: RoundName):
        self.git.apply_code_changes(self.output_path, round_name)


def _format_cov_report(cov_report: dict):
    formatted = {
        "files": {}
    }
    for key, val in cov_report.items():
        if key != "files":
            formatted[key] = val

    if "meta" in formatted:
        formatted["meta"].pop("timestamp", None)

    for file, file_data in cov_report.get("files", {}).items():
        formatted["files"][file.replace("\\", "/")] = file_data

    return json.dumps(formatted, indent=2)


def _save_empty_test_report(exit_code: int, test_report_path: Path):
    test_report = {
        "exitcode": exit_code,
        "summary": {
            "total": 0,
            "collected": 0,
        },
        "collectors": [],
        "tests": [],
    }
    test_report_path.write_text(json.dumps(test_report, indent=2))


def _save_empty_cov_report(cov_report_path: Path):
    cov_report = {
        "meta": {},
        "files": {},
        "totals": {
            "covered_lines": 0,
            "percent_covered": 0,
        }
    }
    cov_report_path.write_text(json.dumps(cov_report, indent=2))
