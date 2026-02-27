# -*- coding: utf-8 -*-

"""
unit tests for eparse cli
"""

import pytest
import plac
import io
import sys

from eparse.cli import main


def test_main():
    # Capture stdout
    stdout = io.StringIO()
    sys.stdout = stdout
    try:
        plac.call(main, ["--help"])
        output = stdout.getvalue()
        assert "Usage" in output
    finally:
        sys.stdout = sys.__stdout__


def test_scan():
    stdout = io.StringIO()
    sys.stdout = stdout
    try:
        plac.call(main, ["-f", "tests/", "scan"])
        output = stdout.getvalue()
        assert "eparse_unit_test_data" in output
    finally:
        sys.stdout = sys.__stdout__


def test_parse():
    stdout = io.StringIO()
    sys.stdout = stdout
    try:
        plac.call(main, ["-f", "tests/", "parse"])
        output = stdout.getvalue()
        assert "eparse_unit_test_data" in output
    finally:
        sys.stdout = sys.__stdout__


def test_query():
    stdout = io.StringIO()
    sys.stdout = stdout
    try:
        plac.call(main, ["-i", "sqlite3:///tests/test.db", "query"])
        output = stdout.getvalue()
        assert output == ""
    finally:
        sys.stdout = sys.__stdout__


def test_migrate():
    stdout = io.StringIO()
    sys.stdout = stdout
    try:
        result = plac.call(
            main,
            ["-i", "sqlite3:///tests/test.db", "migrate", "-m", "migration_000102_000200"]
        )
        output = stdout.getvalue()
        assert result == 1  # Assuming main returns 1 for this case
        assert "duplicate column name: timestamp" in output
    finally:
        sys.stdout = sys.__stdout__


def test_outputs():
    stdout = io.StringIO()
    sys.stdout = stdout
    try:
        plac.call(main, ["-o", "null:///", "scan"])
        output = stdout.getvalue()
        assert output == ""

        stdout = io.StringIO()
        sys.stdout = stdout
        plac.call(main, ["-o", "stdout:///", "scan"])
        output = stdout.getvalue()
        assert output == ""

        stdout = io.StringIO()
        sys.stdout = stdout
        plac.call(main, ["-o", "sqlite3:///:memory:", "scan"])
        output = stdout.getvalue()
        assert output == ""

        stdout = io.StringIO()
        sys.stdout = stdout
        result = plac.call(main, ["-o", "test", "scan"])
        assert result == 1  # Assuming main returns 1 for this case
        output = stdout.getvalue()
        assert "test is not a recognized endpoint" in output

        with pytest.raises(ValueError):
            plac.call(main, ["-d", "-o", "test", "scan"])
    finally:
        sys.stdout = sys.__stdout__
