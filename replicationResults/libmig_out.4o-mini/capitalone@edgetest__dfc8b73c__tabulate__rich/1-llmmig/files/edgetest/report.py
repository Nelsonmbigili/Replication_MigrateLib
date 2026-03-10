"""Generate rST reports."""

from typing import Any, List

from rich.console import Console
from rich.table import Table

from edgetest.core import TestPackage

VALID_OUTPUTS = ["rst", "github"]


def gen_report(testers: List[TestPackage], output_type: str = "rst") -> Any:
    """Generate a rST report.

    Parameters
    ----------
    testers : list
        A list of ``TestPackage`` objects.

    output_type : str
        A valid output type of ``rst`` or ``github``

    Returns
    -------
    Any
        The report.
    """
    if output_type not in VALID_OUTPUTS:
        raise ValueError(f"Invalid output_type provided: {output_type}")

    headers = [
        "Environment",
        "Setup successful",
        "Passing tests",
        "Upgraded packages",
        "Lowered packages",
        "Package version",
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    for header in headers:
        table.add_column(header)

    for env in testers:
        upgraded = env.upgraded_packages()
        lowered = env.lowered_packages()
        for pkg in upgraded:
            table.add_row(
                env.envname,
                str(env.setup_status),
                str(env.status),
                pkg["name"],
                "",
                pkg["version"],
            )
        for pkg in lowered:
            table.add_row(
                env.envname,
                str(env.setup_status),
                str(env.status),
                "",
                pkg["name"],
                pkg["version"],
            )

    console = Console()
    console.print(table)
    return None  # Since we are printing the table, we return None
