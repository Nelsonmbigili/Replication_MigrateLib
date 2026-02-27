import subprocess
from pathlib import Path

from libmig.code_analysis.call_grind_parser import CallGrindParser
from libmig.code_analysis.cg import CG
from libmig.code_analysis.cg_builder import CGBuilder
from libmig.project import Project


def funcs(cg: CG, *func_names):
    return [next(f for f in cg.functions if f.name == fn) for fn in func_names]


def _build_cg(code_file):
    project_root = Path(__file__).parent / "dummy_code"
    script_path = project_root / code_file
    profile_path = script_path.with_suffix(".callgrind")
    venv_path = Path(__file__).parent / "dummy_venv"
    venv_path.mkdir(exist_ok=True)
    cmd_args = ["pprofile", "--exclude-syspath", "--format", "callgrind", "--out", profile_path.as_posix(),
                script_path.as_posix()]
    print(" ".join(cmd_args))
    res = subprocess.run(cmd_args)
    assert res.returncode == 0, f"Failed to run pprofile on {script_path}"
    project = Project("x", "y", project_root, venv_path=venv_path)

    parser = CallGrindParser(profile_path.read_text())
    raw_calls = parser.parse()

    builder = CGBuilder(raw_calls, project)
    cg = builder.build()
    venv_path.rmdir()
    profile_path.unlink()
    return cg


def assert_all_empty_direct(*functions):
    for f in functions:
        assert f.direct_callees == set(), f"{f.name} has non-empty direct callees"


def assert_all_empty_transitive(*functions):
    for f in functions:
        assert f.transitive_callees == set(), f"{f.name} has non-empty transitive callees"


def test_function_props():
    cg = _build_cg("simple_acyclic.py")
    a = funcs(cg, "a")[0]
    assert a.name == "a"
    assert a.file == "simple_acyclic.py"
    assert a.owner == "client"
    assert a.line == 1
    assert a.qualified_name == "a"


def test_simple_acyclic_cg():
    cg = _build_cg("simple_acyclic.py")

    a, b, c = funcs(cg, "a", "b", "c")
    assert a.direct_callees == {b, c}
    assert_all_empty_direct(b, c)
    assert_all_empty_transitive(a, b, c)


def test_simple_cyclic_transitive_cg_1():
    cg = _build_cg("simple_acyclic_transitive_1.py")

    a, b, c = funcs(cg, "a", "b", "c")
    assert a.direct_callees == {b}
    assert b.direct_callees == {c}
    assert_all_empty_direct(c)

    assert a.transitive_callees == {c}
    assert_all_empty_transitive(b, c)


def test_simple_cyclic_transitive_cg_2():
    cg = _build_cg("simple_acyclic_transitive_2.py")

    a, b, c = funcs(cg, "a", "b", "c")
    assert a.direct_callees == {b, c}
    assert b.direct_callees == {c}
    assert_all_empty_direct(c)
    assert_all_empty_transitive(a, b, c)


def test_complex_acyclic():
    cg = _build_cg("complex_acyclic.py")

    a, b, c, d, e, f, g = funcs(cg, "a", "b", "c", "d", "e", "f", "g")
    assert a.direct_callees == {b, c}
    assert b.direct_callees == {c, d}
    assert d.direct_callees == {e}
    assert e.direct_callees == {f, g}
    assert_all_empty_direct(c, f, g)

    assert a.transitive_callees == {d, e, f, g}
    assert b.transitive_callees == {e, f, g}
    assert d.transitive_callees == {f, g}
    assert_all_empty_transitive(e, f, g)


def test_cyclic_self():
    cg = _build_cg("cyclic_self.py")

    a = funcs(cg, "a")[0]
    assert a.direct_callees == {a}
    assert a.transitive_callees == set()


def test_cyclic_2level():
    cg = _build_cg("cyclic_2level.py")

    a, b = funcs(cg, "a", "b")
    assert a.direct_callees == {b}
    assert b.direct_callees == {a}

    assert a.transitive_callees == {a}
    assert b.transitive_callees == {b}


def test_def_with_decorators():
    cg = _build_cg("function_def_with_decorators.py")

    a = funcs(cg, "a")[0]
    assert a.line == 9
