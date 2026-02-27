"""Test the CLI."""

import platform
from pathlib import Path
from unittest.mock import PropertyMock, call, patch

from typer.testing import CliRunner  # Updated import to use typer.testing

from edgetest.interface import cli

CURR_DIR = Path(__file__).resolve().parent

REQS = """
myupgrade
"""

SETUP_TOML = """
[edgetest.envs.myenv]
upgrade = ["myupgrade"]
command = "pytest tests -m 'not integration'"
"""

SETUP_TOML_LOWER = """
[project]
dependencies = ["myupgrade<=0.1.5", "mylower<=0.1.0,>=0.0.1"]

[edgetest.envs.myenv_lower]
lower = ["mylower"]
command = "pytest tests -m 'not integration'"
"""

SETUP_TOML_REQS = """
[project]
dependencies = ["myupgrade<=0.1.5"]
"""

SETUP_TOML_REQS_UPGRADE = """
[project]
dependencies = ["myupgrade<=0.2.0"]
"""

SETUP_TOML_EXTRAS = """
[project.optional-dependencies]
myextra = ["myupgrade<=0.1.5"]

[edgetest.envs.myenv]
upgrade = ["myupgrade"]
extras = ["myextra"]
command = "pytest tests -m 'not integration'"
"""


SETUP_TOML_EXTRAS_UPGRADE = """
[project.optional-dependencies]
myextra = ["myupgrade<=0.2.0"]

[edgetest.envs.myenv]
upgrade = ["myupgrade"]
extras = ["myextra"]
command = "pytest tests -m 'not integration'"
"""

PIP_LIST = """
[{"name": "myupgrade", "version": "0.2.0"}]
"""

TABLE_OUTPUT = """

=============  ==================  ===============  ===================  ==================  =================
Environment    Setup successful    Passing tests    Upgraded packages    Lowered packages    Package version
=============  ==================  ===============  ===================  ==================  =================
myenv          True                True             myupgrade                                0.2.0
=============  ==================  ===============  ===================  ==================  =================
"""

TABLE_OUTPUT_LOWER = """

=============  ==================  ===============  ===================  ==================  =================
Environment    Setup successful    Passing tests    Upgraded packages    Lowered packages    Package version
=============  ==================  ===============  ===================  ==================  =================
myenv_lower    True                True                                  mylower             0.0.1
=============  ==================  ===============  ===================  ==================  =================
"""

TABLE_OUTPUT_NOTEST = """

=============  ==================  ===============  ===================  ==================  =================
Environment    Setup successful    Passing tests    Upgraded packages    Lowered packages    Package version
=============  ==================  ===============  ===================  ==================  =================
myenv          True                False            myupgrade                                0.2.0
=============  ==================  ===============  ===================  ==================  =================
"""

TABLE_OUTPUT_NOTEST_LOWER = """

=============  ==================  ===============  ===================  ==================  =================
Environment    Setup successful    Passing tests    Upgraded packages    Lowered packages    Package version
=============  ==================  ===============  ===================  ==================  =================
myenv_lower    True                False                                 mylower             0.0.1
=============  ==================  ===============  ===================  ==================  =================
"""

TABLE_OUTPUT_REQS = """

================  ==================  ===============  ===================  ==================  =================
Environment       Setup successful    Passing tests    Upgraded packages    Lowered packages    Package version
================  ==================  ===============  ===================  ==================  =================
myupgrade         True                True             myupgrade                                0.2.0
all-requirements  True                True             myupgrade                                0.2.0
================  ==================  ===============  ===================  ==================  =================
"""


@patch("edgetest.lib.EnvBuilder", autospec=True)
@patch("edgetest.core.Popen", autospec=True)
@patch("edgetest.utils.Popen", autospec=True)
def test_cli_basic(mock_popen, mock_cpopen, mock_builder):
    """Test creating a basic environment."""
    mock_popen.return_value.communicate.return_value = (PIP_LIST, "error")
    type(mock_popen.return_value).returncode = PropertyMock(return_value=0)
    mock_cpopen.return_value.communicate.return_value = ("output", "error")
    type(mock_cpopen.return_value).returncode = PropertyMock(return_value=0)

    runner = CliRunner()

    with runner.isolated_filesystem() as loc:
        with open("pyproject.toml", "w") as outfile:
            outfile.write(SETUP_TOML)

        result = runner.invoke(cli, ["--config=pyproject.toml"])

    assert result.exit_code == 0

    env_loc = Path(loc) / ".edgetest" / "myenv"
    if platform.system() == "Windows":
        py_loc = env_loc / "Scripts" / "python.exe"
    else:
        py_loc = env_loc / "bin" / "python"

    mock_builder.return_value.create.assert_called_with(env_loc)
    assert mock_popen.call_args_list == [
        call(
            ("uv", "pip", "install", f"--python={py_loc!s}", "."),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
        call(
            (
                "uv",
                "pip",
                "install",
                f"--python={py_loc!s}",
                "myupgrade",
                "--upgrade",
            ),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
        call(
            ("uv", "pip", "list", f"--python={py_loc!s}", "--format", "json"),
            stdout=-1,
            stderr=-1,
            universal_newlines=True,
        ),
    ]
    assert mock_cpopen.call_args_list == [
        call(
            (
                f"{py_loc!s}",
                "-m",
                "pytest",
                "tests",
                "-m",
                "not integration",
            ),
            universal_newlines=True,
        )
    ]

    assert result.output == TABLE_OUTPUT


# The rest of the code remains unchanged, except for the import of `typer.testing.CliRunner`.
