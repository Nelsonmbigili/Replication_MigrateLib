import os
from os import PathLike
from typing import Callable


def parse_element_id(id_line: str):
    """
    Parse an element id from a line in the callgrind profile data
    The line can be of the form "fl=..." or "fn=..." or "cfl=..." or "cfn=..." indicating
    a caller file or caller function or callee file or callee function respectively.
    The part after the '=' is the id.
    :param id_line: a line from the callgrind profile data
    :return: the id
    """
    type, id = id_line.strip().split('=')
    id = id.strip()
    if type in {"fl", "cfl"}:
        if not os.path.exists(id):
            name, ext = os.path.splitext(id)
            if "_" in ext:
                actual_ext = ext.split("_")[0]
                id = name + actual_ext
    return id


class RawCall:
    def __init__(self, caller_file: str, caller_func: str, callee_file: str, callee_func: str, call_line: int):
        self.caller_file = caller_file
        self.caller_func = caller_func
        self.callee_file = callee_file
        self.callee_func = callee_func
        self.call_line = call_line

        caller_func_parts = caller_func.split(':')
        self.caller_func_name = caller_func_parts[0]
        self.caller_func_line = int(caller_func_parts[1])

        callee_func_parts = callee_func.split(':')
        self.callee_func_name = callee_func_parts[0]
        self.callee_func_line = int(callee_func_parts[1])

    def __str__(self):
        return f"{self.caller_func} -> {self.callee_func} @ {self.caller_file}:{self.call_line}"


class CallGrindParser:
    def __init__(self, call_grind_data: str | list[str], include_caller: Callable[[str], bool] = None,
                 include_callee: Callable[[str], bool] = None):
        self.lines = call_grind_data.splitlines(keepends=False) if isinstance(call_grind_data, str) else call_grind_data
        self.include_caller = include_caller or (lambda _: True)
        self.include_callee = include_callee or (lambda _: True)
        self._code_lines_index: dict[str, list[str]] = {}

    def parse(self) -> list[RawCall]:
        """
        Minimalistic parse callgrind profile data. We only collect the calls.
        :param call_grind_data: the callgrind profile data
        :return: a list of calls in the profile data
        """
        calls = []
        lines = self.lines

        caller_file: str | None = None
        caller_func: str | None = None
        callee_file: str | None = None
        callee_func: str | None = None
        collect_call = False
        for line in lines:
            if line.startswith("fl="):
                caller_file = parse_element_id(line)
            elif line.startswith("fn="):
                caller_func = parse_element_id(line)
            elif line.startswith('cfl='):
                callee_file = parse_element_id(line)
            elif line.startswith('cfn='):
                callee_func = parse_element_id(line)
            elif line.startswith('calls='):
                collect_call = True
            elif collect_call:
                if not self.include_caller(caller_file) or not self.include_callee(callee_file):
                    collect_call = False
                    continue
                call_line = int(line.split(" ")[0])
                call = RawCall(caller_file, caller_func, callee_file, callee_func, call_line)
                call.caller_func_line = self._resolve_actual_def_line(call.caller_func_line, call.caller_file,
                                                                      call.caller_func_name)
                call.callee_func_line = self._resolve_actual_def_line(call.callee_func_line, call.callee_file,
                                                                      call.callee_func_name)
                calls.append(call)
                collect_call = False

        return calls

    def _resolve_actual_def_line(self, line_in_cg: int, file: str, func_name: str):
        """
        If a function definition has decorators,
        then the line number in the call graph is the line number of the first decorator,
        not the line where the function is actually defined.
        For example, in the below code, the line number in the call graph for `f` will be 1, instead of 2.

        This function resolves the actual line number of the function definition, so for the below code, it will return 2.

        ```
        @decorator      # line 1
        def f():        # line 2
            pass        # line 3
        ```
        :param file:
        :param line_in_cg:
        :param func_name:
        :return:
        """
        if func_name[0] == "<" and func_name[-1] == ">":
            # this is a system function or <module>
            return line_in_cg

        if file[0] == "<" and file[-1] == ">":
            # this is a system code
            return line_in_cg

        if file not in self._code_lines_index:
            # extra line to make line numbers 1-based
            try:
                self._code_lines_index[file] = [""] + open(file, "r", encoding="utf8").readlines()
            except Exception as e:
                print(f"Error reading file {file}: {e}")

        lines: list[str] = self._code_lines_index[file]

        def_line = line_in_cg
        while True:
            if def_line >= len(lines):
                return -1  # in some cases, the callgrind profile data is not correct. not sure why.
            code_at_line = lines[def_line].strip()
            if func_name in code_at_line:
                if "def " in code_at_line or "class " in code_at_line:
                    break
            def_line += 1

        return def_line
