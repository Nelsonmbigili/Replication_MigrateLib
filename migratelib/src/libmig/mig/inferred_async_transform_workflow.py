import shutil
from collections import defaultdict

import libcst as cst
from libcst import ParserSyntaxError

from libmig.code_analysis.async_transformer import AsyncTransformer
from libmig.code_analysis.cg import CGFunction, CGCall
from libmig.code_analysis.cg_builder import build_from_profile
from libmig.code_analysis.cst_mapping import CSTMapping, CSTMapper
from libmig.code_analysis.qualified_name_index import QualifiedNameIndex
from libmig.mig.mig_error import MigError, ErrorCode
from libmig.mig.mig_report_models import RoundName
from libmig.project import Project
from libmig.utils.cgx import CGX


def find_transitive_call_info(asynced_functions: list[CSTMapping], cg: CGX):
    asynced_cg_funcs = {cg.find_client_function(mapping.file, mapping.qualified_name) for mapping in asynced_functions}
    asynced_cg_funcs = {func for func in asynced_cg_funcs if func is not None}
    # some functions are not part of the call graph because they are not called at all. we remove them.

    all_cg_funcs_to_async = set(asynced_cg_funcs)
    for cg_func in asynced_cg_funcs:
        all_cg_funcs_to_async.update(cg_func.all_callers)

    all_cg_calls_to_await = set()
    for cg_func in all_cg_funcs_to_async:
        all_cg_calls_to_await.update(cg_func.direct_calls_to_me)

    return all_cg_funcs_to_async, all_cg_calls_to_await


class InferredAsyncTransformWorkflow:
    def __init__(self, project: Project):
        """
        Apply async transformations to the codebase based on changes in the given base round
        :param project:
        :param base_round_name:
        """
        self.mig_files = None
        self.tests_to_async = None
        self.calls_to_await = None
        self.funcs_to_async = None
        self.project = project
        self.mig_log = self.project.get_loger()

        self.premig_qname_mappers: dict[str, QualifiedNameIndex] = {}
        self.base_round_qname_mappers: dict[str, QualifiedNameIndex] = {}

    @property
    def _cg(self):
        if not hasattr(self, "_cg_instance"):
            self._cg_instance = build_from_profile(self.project, "premig")
        return self._cg_instance

    @property
    def _report(self):
        if not hasattr(self, "_report_instance"):
            self._report_instance = self.project.get_report()
        return self._report_instance

    @property
    def base_round_name(self):
        if not hasattr(self, "_base_round_name_instance"):
            self._base_round_name_instance = self._report.get_best_round(["llmmig", "merge_skipped"]) or "llmmig"
        return self._base_round_name_instance

    def _premig_qname_index(self, file: str) -> QualifiedNameIndex:
        if file not in self.premig_qname_mappers:
            module = cst.parse_module(self.project.premig_paths.read_code_file(file))
            self.premig_qname_mappers[file] = QualifiedNameIndex(module)
        return self.premig_qname_mappers[file]

    def _project_file_qname_index(self, file: str) -> QualifiedNameIndex:
        git_repo = self.project.git
        if file not in self.base_round_qname_mappers:
            file_path = git_repo.file_path(file)
            try:
                module = cst.parse_module(file_path.read_text("utf-8"))
            except ParserSyntaxError as e:
                raise MigError(ErrorCode.LLM_SYNTAX_ERROR, "syntax error in LLM migrated file", str(e))
            self.base_round_qname_mappers[file] = QualifiedNameIndex(module)
        return self.base_round_qname_mappers[file]

    def run(self):
        funcs_to_async_by_file = _group_by_file(self.funcs_to_async)
        calls_to_await_by_file = _group_by_file(self.calls_to_await)
        tests_to_async_by_file = _group_by_file(self.tests_to_async)
        self.project.apply_code_changes(self.base_round_name)
        self.mig_log.log_event(f"{len(self.mig_files)} files requires transformation", "l1")

        mig_files = set(self.mig_files)

        current_files_root = self.project.round_paths("async_transform").files_root
        if current_files_root.exists():
            shutil.rmtree(current_files_root, ignore_errors=True)

        git_repo = self.project.git
        for file in mig_files:
            self.mig_log.log_event(f"transforming {file}", "l1")
            self.project.premig_paths.copy_file(file, git_repo.file_path(file))
            qname_index = self._project_file_qname_index(file)

            transformer = AsyncTransformer(funcs_to_async_by_file[file], calls_to_await_by_file[file],
                                           tests_to_async_by_file[file], qname_index)
            module_wrapper = cst.MetadataWrapper(qname_index.module)
            transformed_module = module_wrapper.visit(transformer)
            transformed_code = transformed_module.code

            # transformer.check_processed_all()
            self.project.async_paths.write_code_file(file, transformed_code)

        self.project.venv.install("pytest-asyncio", "latest")

    def find_mig_locations(self):
        self.mig_log.log_event(f"Running inferred async transform", "h2")
        self.project.apply_code_changes(self.base_round_name)
        asynced_funcs = self.find_asynced_functions()

        self.mig_log.log_event(f"Finding async transforms", "h3")
        cg_funcs_to_async, cg_calls_to_await = find_transitive_call_info(asynced_funcs, self._cg)
        premig_test_report = self.project.premig_paths.read_utest_report()
        names_of_funcs_to_async = {func.name for func in cg_funcs_to_async}
        tests_to_async = {self._cg.find_test_function(utest) for utest in premig_test_report.tests if
                          utest.function_name in names_of_funcs_to_async}
        self.mig_log.log_event(
            f"Found {len(cg_funcs_to_async)} functions to mark async including {len(tests_to_async)} tests", "l1")
        self.mig_log.log_event(f"Found {len(cg_calls_to_await)} calls to await", "l1")
        self.funcs_to_async = cg_funcs_to_async
        self.calls_to_await = cg_calls_to_await
        self.tests_to_async = tests_to_async
        self.mig_files = {func.file for func in cg_funcs_to_async} | {call.caller.file for call in cg_calls_to_await}

        return self.mig_files

    def find_asynced_functions(self):
        base_round_paths = self.project.round_paths(self.base_round_name).mig_code_files

        asynced_functions = []
        for file_path in base_round_paths:
            index_before = self._premig_qname_index(file_path)
            index_after = self._project_file_qname_index(file_path)
            cst_mapper = CSTMapper(file_path, index_before, index_after)
            asynced_functions += cst_mapper.asynced_functions()

        return asynced_functions


def _group_by_file(funcs: set[CGFunction | CGCall]) -> dict[str, set[CGFunction | CGCall]]:
    groups = defaultdict(set)
    for item in funcs:
        if not item:
            continue
        file = item.file if isinstance(item, CGFunction) else item.caller.file
        groups[file].add(item)

    return groups
