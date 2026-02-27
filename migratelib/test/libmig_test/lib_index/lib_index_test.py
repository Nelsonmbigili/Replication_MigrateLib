from pathlib import Path

import pytest

from libmig.lib_index.lib_index import LibIndex


def test_lib_index__non_builtin_lib1():
    index = LibIndex("typer", "0.15.1")
    assert index.get_api("Argument")
    assert index.get_api("Option")
    assert index.get_api("Typer")

    with pytest.raises(ValueError) as e:
        index.get_api("something_that_does_not_exist")
        assert "not found" in str(e.value)


def test_lib_index__non_builtin_lib2():
    index = LibIndex("pyyaml", "6.0")
    assert index.get_api("safe_load")


def test_api_doc__found():
    index = LibIndex("typer", "0.15.1")
    api = index.get_api("echo")
    assert "Print a message" in api.doc

# TODO: test with ambiguous API name
