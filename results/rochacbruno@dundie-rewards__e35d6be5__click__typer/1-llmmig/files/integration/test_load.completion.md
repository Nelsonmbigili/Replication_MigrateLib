### Explanation of Changes
To migrate the code from using the `click` library to `typer`, the following changes were made:
1. Replaced `click.testing.CliRunner` with `typer.testing.CliRunner`, as `typer` provides its own testing utilities that are compatible with `click`-style commands.
2. Updated the import statements to use `typer.testing` instead of `click.testing`.
3. No changes were made to the logic of the tests or the commands, as `typer` is built on top of `click` and supports similar command-line interface structures.

### Modified Code
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

### Summary
The migration involved replacing `click.testing.CliRunner` with `typer.testing.CliRunner` and updating the corresponding import statement. No other changes were necessary, as the rest of the code remains compatible with `typer`.