### Explanation of Changes
To migrate the code from using the `click` library to the `plac` library, the following changes were made:

1. **Import Statement**: The import for `CliRunner` from `click.testing` was removed, as `plac` does not have a direct equivalent.
2. **Command Invocation**: The `invoke` method used with `CliRunner` in `click` was replaced with direct function calls, as `plac` does not require a runner for command invocation.
3. **Parameter Handling**: The way parameters are passed to the command functions was adjusted to fit the `plac` style, which uses function signatures directly.

### Modified Code
```python
import pytest
from dundie.cli import load, main

from .constants import PEOPLE_FILE


@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """test command load"""
    out = load(PEOPLE_FILE)
    assert "Dunder Mifflin Associates" in out


@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.parametrize("wrong_command", ["loady", "carrega", "start"])
def test_load_negative_call_load_command_with_wrong_params(wrong_command):
    """test command load"""
    with pytest.raises(SystemExit) as excinfo:
        main(wrong_command, PEOPLE_FILE)
    assert excinfo.value.code != 0
    assert f"No such command '{wrong_command}'." in str(excinfo.value)
``` 

In this modified code, the `load` function is called directly with the `PEOPLE_FILE` argument, and the `main` function is called within a context manager to catch the `SystemExit` exception that `plac` raises for invalid commands.