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
