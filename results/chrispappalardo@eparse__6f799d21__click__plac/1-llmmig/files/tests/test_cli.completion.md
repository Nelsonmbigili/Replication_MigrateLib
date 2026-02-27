### Explanation of Changes:
The original code uses the `click` library for command-line interface (CLI) testing via `CliRunner`. To migrate to the `plac` library, the following changes were made:
1. **Replace `CliRunner` with direct invocation of the `plac`-based `main` function**:
   - `plac` does not have a testing utility like `CliRunner`. Instead, the `plac.call()` function is used to directly invoke the `main` function with arguments.
   - The `plac.call()` function takes a callable (e.g., `main`) and a list of arguments as input.
2. **Remove `kwargs`**:
   - The `kwargs` dictionary (used for `click`'s `invoke` method) is no longer needed because `plac` does not support such options.
3. **Adjust assertions**:
   - `plac.call()` does not return an object with `exit_code` or `output`. Instead, the return value of the `main` function is captured directly, and any output to `stdout` or `stderr` must be captured using Python's `io.StringIO`.

### Modified Code:
```python
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
```

### Key Notes:
1. **Capturing Output**:
   - Since `plac` does not provide a built-in mechanism to capture CLI output, Python's `io.StringIO` is used to temporarily redirect `sys.stdout` and capture the output.
   - After each test, `sys.stdout` is restored to its original value (`sys.__stdout__`).
2. **Exit Codes**:
   - `plac.call()` returns the return value of the `main` function. If `main` uses `sys.exit()` to set an exit code, it must be handled appropriately in the tests.
3. **Assertions**:
   - Assertions on `result.exit_code` and `result.output` are replaced with checks on the return value of `plac.call()` and the captured `stdout` content.