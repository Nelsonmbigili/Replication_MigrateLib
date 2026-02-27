import ast
import warnings
from pathlib import Path

from libmig.code_analysis.call_grind_parser import RawCall, CallGrindParser
from libmig.code_analysis.qualified_name_index import QualifiedNameIndex
from libmig.mig.mig_report_models import RoundName
from libmig.project import Project
from libmig.utils.cgx import CGX


class CGBuilder:
    def __init__(self, raw_calls: list[RawCall], project: Project):
        self.raw_calls = raw_calls
        self.project = project
        self.cg = CGX()
        self._qname_index_map = {}

    def _get_qname_index(self, file: Path) -> QualifiedNameIndex:
        if file not in self._qname_index_map:
            qname_index = QualifiedNameIndex(file.read_text("utf-8"))
            self._qname_index_map[file] = qname_index
        return self._qname_index_map[file]

    def build(self) -> CGX:
        self._build_direct_calls()
        self._build_transitive_calls()
        return self.cg

    def _build_direct_calls(self):
        cg = self.cg
        raw_calls = self.raw_calls
        project = self.project
        for r_call in raw_calls:
            callee_path = Path(r_call.callee_file)
            if project.is_client_code(callee_path):
                to_owner = "client"
                callee_rpath = callee_path.relative_to(project.code_path)
            elif callee_rpath := project.path_in_source_lib(callee_path):
                to_owner = project.source
            else:
                continue

            caller_path = Path(r_call.caller_file)
            caller_qname = self._get_qname_index(caller_path).get_qname_at(r_call.caller_func_line)

            caller_path = caller_path.relative_to(project.code_path).as_posix()
            caller = cg.add_function(owner="client", file=caller_path, line=r_call.caller_func_line,
                                     name=r_call.caller_func_name, qualified_name=caller_qname)

            callee_qname = self._get_qname_index(callee_path).get_qname_at(r_call.callee_func_line)
            callee = cg.add_function(owner=to_owner, file=callee_rpath.as_posix(), line=r_call.callee_func_line,
                                     name=r_call.callee_func_name, qualified_name=callee_qname)

            cg.add_direct_call(caller, callee, r_call.call_line)

    def _build_transitive_calls(self):
        cg = self.cg
        import networkx as nx
        graph = nx.DiGraph()
        direct_calls_without_call_line = {(call.caller, call.callee) for call in cg.direct_calls}
        graph.add_edges_from(direct_calls_without_call_line)

        transitive_closure = nx.transitive_closure(graph)
        raw_transitive_calls = set(transitive_closure.edges) - direct_calls_without_call_line

        for caller, callee in raw_transitive_calls:
            cg.add_transitive_call(caller, callee)


def build_from_profile(project: Project, round_name: RoundName) -> CGX:
    git_repo = project.git
    if not hasattr(project, "cgs"):
        project.cgs = {}

    if round_name in project.cgs:
        return project.cgs[round_name]

    paths = project.round_paths(round_name)
    print(f"Building CG from profile report")

    project.apply_code_changes(round_name)
    if not paths.profile_report.exists():
        print(f"Profile report not found, running tests to generate profile report")
        utest_script = project.code_path.joinpath("_run_tests_.py")
        utest_script.write_text("import pytest\npytest.main()")
        project.venv.run_script("pprofile", "--exclude-syspath", "--format", "callgrind", "--out",
                                paths.profile_report.as_posix(), utest_script.as_posix(), read_output=False,
                                cwd=project.code_path)

    def caller_file_filter(file: str):
        return project.is_client_code(Path(file))

    def callee_file_filter(file: str):
        return project.is_client_code(Path(file)) or project.path_in_source_lib(Path(file))

    raw_calls = CallGrindParser(paths.profile_report.read_text(), caller_file_filter, callee_file_filter).parse()
    builder = CGBuilder(raw_calls, project)
    cg = builder.build()
    project.cgs[round_name] = cg

    return project.cgs[round_name]
