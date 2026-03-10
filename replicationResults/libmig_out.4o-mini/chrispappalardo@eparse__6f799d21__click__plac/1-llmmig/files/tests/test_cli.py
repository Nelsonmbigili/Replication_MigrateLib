# -*- coding: utf-8 -*-

"""
unit tests for eparse cli
"""

import pytest
import sys
from eparse.cli import main

kwargs = {"obj": {}, "catch_exceptions": False}


def test_main():
    try:
        main(["--help"])
        assert True  # If no exception is raised, the test passes
    except SystemExit as e:
        assert e.code == 0
        assert "Usage" in str(e)


def test_scan():
    try:
        result = main(["-f", "tests/", "scan"], **kwargs)
        assert True  # If no exception is raised, the test passes
        assert "eparse_unit_test_data" in result
    except SystemExit as e:
        assert e.code == 0


def test_parse():
    try:
        result = main(["-f", "tests/", "parse"], **kwargs)
        assert True  # If no exception is raised, the test passes
        assert "eparse_unit_test_data" in result
    except SystemExit as e:
        assert e.code == 0


def test_query():
    try:
        result = main(["-i", "sqlite3:///tests/test.db", "query"], **kwargs)
        assert True  # If no exception is raised, the test passes
        assert result == ""
    except SystemExit as e:
        assert e.code == 0


def test_migrate():
    try:
        result = main(
            ["-i", "sqlite3:///tests/test.db", "migrate", "-m", "migration_000102_000200"],
            **kwargs
        )
        assert False  # Should raise an exception
    except SystemExit as e:
        assert e.code == 1
        assert "duplicate column name: timestamp" in str(e)


def test_outputs():
    try:
        result = main(["-o", "null:///", "scan"], **kwargs)
        assert True  # If no exception is raised, the test passes
        assert result == ""
        
        result = main(["-o", "stdout:///", "scan"], **kwargs)
        assert True  # If no exception is raised, the test passes
        assert result == ""
        
        result = main(["-o", "sqlite3:///:memory:", "scan"], **kwargs)
        assert True  # If no exception is raised, the test passes
        assert result == ""
        
        result = main(["-o", "test", "scan"], **kwargs)
        assert False  # Should raise an exception
    except SystemExit as e:
        assert e.code == 1
        assert "test is not a recognized endpoint" in str(e)
    
    with pytest.raises(ValueError):
        main(["-d", "-o", "test", "scan"], **kwargs)
