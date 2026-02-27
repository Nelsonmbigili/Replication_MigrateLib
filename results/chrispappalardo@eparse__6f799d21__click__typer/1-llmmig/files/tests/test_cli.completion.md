### Explanation of Changes

To migrate the code from using the `click` library to `typer`, the following changes were made:

1. **`CliRunner` Replacement**: The `click.testing.CliRunner` is replaced with `typer.testing.CliRunner`, as `typer` provides its own testing utilities that are compatible with `click`'s testing interface.
2. **Import Adjustments**: The `click.testing` import is replaced with `typer.testing`.
3. **No Changes to Functionality**: Since `typer` is built on top of `click`, the `main` function (assumed to be a `typer` app) and its invocation remain the same. The migration only involves replacing the testing utilities.

Below is the modified code:

---

### Modified Code
```python
# -*- coding: utf-8 -*-

"""
unit tests for eparse cli
"""

import pytest
from typer.testing import CliRunner  # Updated import to use typer's testing utilities

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

---

### Summary of Changes
- Replaced `click.testing.CliRunner` with `typer.testing.CliRunner`.
- Updated the import statement to use `typer.testing`.
- No other changes were made to the code, as `typer` is compatible with `click`'s interface for testing.