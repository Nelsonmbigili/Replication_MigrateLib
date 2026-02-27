import ast
import warnings

from libmig.code_analysis.cg import CGFunction, CG
from libmig.utest import UTestReportDiff, UTestItem
from libmig.utest.utest_report_diff import UTestItemDiff


class CGX(CG):

    def find_failed_tests_for_file(self, utest_report_diff: UTestReportDiff, client_file: str):
        for item_diff in utest_report_diff.diffs:
            tested_client_functions = self.find_client_calls_from_test(item_diff)
            callee_files = {client_func.file for client_func in tested_client_functions}
            if client_file in callee_files:
                yield item_diff

    def find_files_with_test_error(self, utest_report_diff: UTestReportDiff):
        files = set()
        for item_diff in utest_report_diff.diffs:
            tested_client_functions = self.find_client_calls_from_test(item_diff)
            callee_files = {client_func.file for client_func in tested_client_functions}
            files.update(callee_files)

        return files

    def find_test_function(self, utest: UTestItem):
        candidates = [func for func in self.functions if
                      func.file == utest.filepath and func.name == utest.function_name]
        if len(candidates) > 1:
            # line numbers are often off by a few lines, so we need a range check
            candidates = [func for func in candidates if -3 < func.line - utest.lineno < 3]

        if not candidates:
            return None
        if len(candidates) > 1:
            raise ValueError(f"Multiple functions with the same name and file: {candidates}")

        return candidates[0]

    def find_client_calls_from_test(self, utest_diff: UTestItemDiff) -> set[CGFunction]:
        utest_func = self.find_test_function(utest_diff.before)
        if utest_func is None:
            return set()
        return {callee for callee in self.all_callees(utest_func) if callee.owner == "client"}

    def find_lib_calls_from_test(self, utest_diff: UTestItemDiff, lib_name: str) -> set[CGFunction]:
        utest_func = self.find_test_function(utest_diff.before)
        if utest_func is None:
            return set()
        all_callees = self.all_callees(utest_func)
        lib_callees = {callee for callee in all_callees if callee.owner == lib_name}
        return lib_callees

    def find_client_function(self, file: str, qualified_name: str):
        return next((func for func in self.functions if
                     func.owner == "client" and func.file == file and func.qualified_name == qualified_name), None)
