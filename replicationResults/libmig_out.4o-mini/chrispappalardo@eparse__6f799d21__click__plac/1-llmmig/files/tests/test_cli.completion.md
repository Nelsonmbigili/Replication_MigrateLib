### Explanation of Changes
To migrate the code from using the `click` library to the `plac` library, the following changes were made:

1. **Remove `CliRunner`**: The `CliRunner` class from `click.testing` is not available in `plac`. Instead, we will directly call the `main` function with the arguments.
2. **Change Invocation Method**: The `invoke` method used in `CliRunner` is replaced with a direct call to the `main` function, passing the arguments as a list.
3. **Error Handling**: Since `plac` does not have a built-in mechanism for capturing output and exit codes like `click`, we will need to handle the output and exceptions differently. We will use `try-except` blocks to catch exceptions and print outputs directly.

Here is the modified code:

```python
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
```

### Note
The above code assumes that the `main` function in the `eparse.cli` module is compatible with the way `plac` handles command-line arguments. If the `main` function is not designed to return output or raise exceptions in a way that can be captured, further adjustments may be necessary.