import pytest
from plac import Interpreter

from dundie.cli import load, main

from .constants import PEOPLE_FILE

cmd = Interpreter()


@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """test command load"""
    out = cmd.call(load, [PEOPLE_FILE])
    assert "Dunder Mifflin Associates" in out[0]  # Accessing the output from plac


@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.parametrize("wrong_command", ["loady", "carrega", "start"])
def test_load_negative_call_load_command_with_wrong_params(wrong_command):
    """test command load"""
    out = cmd.call(main, [wrong_command, PEOPLE_FILE])
    assert out[1] != 0  # Checking the exit code (plac returns a tuple: (output, exit_code))
    assert f"No such command '{wrong_command}'." in out[0]  # Accessing the output from plac
