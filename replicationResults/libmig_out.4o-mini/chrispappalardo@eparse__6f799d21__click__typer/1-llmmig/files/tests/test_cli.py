# -*- coding: utf-8 -*-

"""
unit tests for eparse cli
"""

import pytest
from eparse.cli import main

def test_main():
    result = main(["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_scan():
    result = main(["-f", "tests/", "scan"])
    assert result.exit_code == 0
    assert "eparse_unit_test_data" in result.output


def test_parse():
    result = main(["-f", "tests/", "parse"])
    assert result.exit_code == 0
    assert "eparse_unit_test_data" in result.output


def test_query():
    result = main(["-i", "sqlite3:///tests/test.db", "query"])
    assert result.exit_code == 0
    assert result.output == ""


def test_migrate():
    result = main(
        ["-i", "sqlite3:///tests/test.db", "migrate", "-m", "migration_000102_000200"]
    )
    assert result.exit_code == 1
    assert "duplicate column name: timestamp" in result.output


def test_outputs():
    result = main(["-o", "null:///", "scan"])
    assert result.exit_code == 0
    assert result.output == ""
    result = main(["-o", "stdout:///", "scan"])
    assert result.exit_code == 0
    assert result.output == ""
    result = main(["-o", "sqlite3:///:memory:", "scan"])
    assert result.exit_code == 0
    assert result.output == ""
    result = main(["-o", "test", "scan"])
    assert result.exit_code == 1
    assert "test is not a recognized endpoint" in result.output
    with pytest.raises(ValueError):
        result = main(["-d", "-o", "test", "scan"])
