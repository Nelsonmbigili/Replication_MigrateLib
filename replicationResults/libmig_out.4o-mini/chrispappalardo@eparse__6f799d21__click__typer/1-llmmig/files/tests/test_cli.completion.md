### Explanation of Changes

To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Statement**: The import for `CliRunner` from `click.testing` was removed, as `typer` does not require a separate runner for command-line interface testing.
2. **Invocation of the CLI**: The `invoke` method from `CliRunner` was replaced with the `app` callable directly from `typer`. In `typer`, you can call the main function directly as it is designed to work seamlessly with function signatures.
3. **Removal of `kwargs`**: The `kwargs` dictionary was removed since `typer` does not require the `obj` and `catch_exceptions` parameters in the same way as `click`.

The modified code is as follows:

```python
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
```

This code now uses `typer` for command-line interface testing, maintaining the original structure and logic of the tests.