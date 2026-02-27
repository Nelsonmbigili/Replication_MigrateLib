The following Python code currently uses the library "click" version 8.1.7.
Migrate this code to use the library "typer" version 0.15.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "click" to "typer".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "click" and "typer".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
# -*- coding: utf-8 -*-

"""
unit tests for eparse cli
"""

import pytest
from click.testing import CliRunner

from eparse.cli import main

kwargs = {"obj": {}, "catch_exceptions": False}


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_scan():
    runner = CliRunner()
    result = runner.invoke(main, ["-f", "tests/", "scan"], **kwargs)
    assert result.exit_code == 0
    assert "eparse_unit_test_data" in result.output


def test_parse():
    runner = CliRunner()
    result = runner.invoke(main, ["-f", "tests/", "parse"], **kwargs)
    assert result.exit_code == 0
    assert "eparse_unit_test_data" in result.output


def test_query():
    runner = CliRunner()
    result = runner.invoke(main, ["-i", "sqlite3:///tests/test.db", "query"], **kwargs)
    assert result.exit_code == 0
    assert result.output == ""


def test_migrate():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["-i", "sqlite3:///tests/test.db", "migrate", "-m", "migration_000102_000200"],
        **kwargs
    )
    assert result.exit_code == 1
    assert "duplicate column name: timestamp" in result.output


def test_outputs():
    runner = CliRunner()
    result = runner.invoke(main, ["-o", "null:///", "scan"], **kwargs)
    assert result.exit_code == 0
    assert result.output == ""
    result = runner.invoke(main, ["-o", "stdout:///", "scan"], **kwargs)
    assert result.exit_code == 0
    assert result.output == ""
    result = runner.invoke(main, ["-o", "sqlite3:///:memory:", "scan"], **kwargs)
    assert result.exit_code == 0
    assert result.output == ""
    result = runner.invoke(main, ["-o", "test", "scan"], **kwargs)
    assert result.exit_code == 1
    assert "test is not a recognized endpoint" in result.output
    with pytest.raises(ValueError):
        result = runner.invoke(main, ["-d", "-o", "test", "scan"], **kwargs)

```