from pathlib import Path

import pytest

__dummy_code_root = Path(__file__).parent / "dummy_code"


def _code_path(file: str):
    return __dummy_code_root.joinpath(file)


def _read_code(file: str):
    return _code_path(file).read_text("utf-8")


@pytest.fixture
def complex_acyclic_path():
    return _read_code("complex_acyclic.py")


@pytest.fixture
def complex_acyclic_code():
    return _read_code("complex_acyclic.py")


@pytest.fixture
def qnames_code():
    return _read_code("qnames.py")
