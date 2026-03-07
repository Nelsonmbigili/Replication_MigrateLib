### Explanation of Changes
To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Statement**: The import for `CliRunner` from `click.testing` was removed, as `typer` does not have a direct equivalent. Instead, we will use `typer.testing.CliRunner`.
2. **Command Invocation**: The method of invoking commands has changed slightly. In `typer`, we use `CliRunner.invoke()` in a similar way, but we need to ensure that the command functions are compatible with `typer`.
3. **Output Handling**: The output handling remains the same, as both libraries provide access to the output through the `output` attribute of the result.

Here is the modified code:

```python
import pytest
from typer.testing import CliRunner

from dundie.cli import load, main

from .constants import PEOPLE_FILE

cmd = CliRunner()


@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """test command load"""
    out = cmd.invoke(load, PEOPLE_FILE)
    assert "Dunder Mifflin Associates" in out.output


@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.parametrize("wrong_command", ["loady", "carrega", "start"])
def test_load_negative_call_load_command_with_wrong_params(wrong_command):
    """test command load"""
    out = cmd.invoke(main, wrong_command, PEOPLE_FILE)
    assert out.exit_code != 0
    assert f"No such command '{wrong_command}'." in out.output
``` 

This code now uses `typer` for command-line interface testing while maintaining the original structure and functionality.