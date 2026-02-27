from typing import Optional

import libcst as cst
from libcst.metadata import PositionProvider, ParentNodeProvider

from libmig.code_analysis.cg import CGCall, CGFunction
from libmig.code_analysis.qualified_name_index import QualifiedNameIndex


def get_func_name(func: cst.BaseExpression):
    if isinstance(func, cst.Call):
        return f"anonymous:call"
    if isinstance(func, cst.Attribute):
        return func.attr.value
    if isinstance(func, cst.Name):
        return func.value
    if isinstance(func, cst.Subscript):
        return f"anonymous:subscript"
    raise ValueError(f"unknown function type: {type(func)}")


class AsyncTransformer(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider, ParentNodeProvider)

    def __init__(self, funcs_to_async: set[CGFunction], calls_to_await: set[CGCall],
                 tests_to_async: set[CGFunction], qualified_name_index: QualifiedNameIndex):
        """

        :param funcs_to_async: qualified names of the functions to make async
        :param calls_to_await:
        :param tests_to_async: qualified names of the test functions to make async
        :param qualified_name_index:
        """
        super().__init__()
        self.funcs_to_async = funcs_to_async
        self.calls_to_await = calls_to_await
        self.tests_to_async = tests_to_async
        self.qualified_name_index = qualified_name_index

        self._funcs_to_async_qnames = set(f.qualified_name for f in funcs_to_async)
        self._tests_to_async_qnames = set(f.qualified_name for f in tests_to_async)
        self._pytest_imported = False

        self._current_caller: Optional[str] = None
        self.has_tests = bool(tests_to_async)

    def _get_line_number(self, node: cst.CSTNode):
        position = self.get_metadata(PositionProvider, node)
        return position.start.line

    def visit_FunctionDef(self, function_def: cst.FunctionDef):
        # this is to help finding a call correctly
        caller_qname = self.qualified_name_index.get_qname_at(self._get_line_number(function_def))
        self._current_caller = caller_qname

    def leave_Call(self, original_call: cst.Call, updated_call: cst.Call):
        # this is approximate. We get the callee by name, which can fail in following cases:
        # 1. there is a different callee with same name
        # 2. the call is made using an alias, therefore, the original function name and the call.func are different
        if not self._current_caller:
            return updated_call

        parent = self.get_metadata(ParentNodeProvider, original_call)
        if isinstance(parent, cst.Await):
            # already awaiting. no need to await.
            return updated_call

        callee_name = get_func_name(original_call.func)

        is_in_await_list = any(call for call in self.calls_to_await if
                               call.caller.qualified_name == self._current_caller and call.callee.name == callee_name)

        if not is_in_await_list:
            return updated_call

        return cst.Await(expression=updated_call)

    def leave_FunctionDef(self, original_func: cst.FunctionDef, updated_func: cst.FunctionDef):
        self._current_caller = None
        line = self._get_line_number(original_func)
        qname = self.qualified_name_index.get_qname_at(line)
        if not self._funcs_to_async_qnames:
            return updated_func

        if qname not in self._funcs_to_async_qnames:
            return updated_func

        self._funcs_to_async_qnames.remove(qname)
        if updated_func.asynchronous is None:
            updated_func = updated_func.with_changes(asynchronous=cst.Asynchronous())

        if qname in self._tests_to_async_qnames:
            updated_func = self._decorate_asyncio(updated_func)

        return updated_func

    def visit_Import(self, node: cst.Import):
        self._try_mark_pytest_import(node)

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module):
        return self._import_pytest(updated_node)

    def _decorate_asyncio(self, updated_func: cst.FunctionDef):
        """Decorate a function definition with @pytest.mark.asyncio"""
        for existing_decorator in updated_func.decorators:
            if (
                    isinstance(existing_decorator.decorator, cst.Attribute) and
                    existing_decorator.decorator.value.value == "pytest" and
                    existing_decorator.decorator.attr.value == "mark.asyncio"
            ):
                # already marked as async
                return updated_func

        decorator = cst.Decorator(
            decorator=cst.Attribute(
                value=cst.Attribute(
                    value=cst.Name("pytest"),
                    attr=cst.Name("mark")
                ),
                attr=cst.Name("asyncio")
            )
        )
        return updated_func.with_changes(decorators=[decorator] + list(updated_func.decorators))

    def _try_mark_pytest_import(self, node: cst.Import):
        if not self.has_tests:
            return
        if self._pytest_imported:
            # Already imported pytest, nothing to check
            return

        # Check if the import already exists
        for alias in node.names:
            if alias.name.value == "pytest":
                self._pytest_imported = True

    def _import_pytest(self, updated_node: cst.Module):
        if not self.has_tests:
            return updated_node

        if self._pytest_imported:
            return updated_node  # Do nothing if import already exists
        new_import = cst.SimpleStatementLine(
            body=[cst.Import(names=[cst.ImportAlias(name=cst.Name("pytest"))])]
        )
        new_body = list(updated_node.body)
        # Insert after last top-level import
        insert_position = 0
        for i, stmt in enumerate(new_body):
            if isinstance(stmt, (cst.SimpleStatementLine, cst.Import, cst.ImportFrom)):
                insert_position = i + 1
        new_body.insert(insert_position, new_import)
        return updated_node.with_changes(body=new_body)
