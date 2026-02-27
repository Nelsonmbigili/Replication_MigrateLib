### Explanation of Changes
To migrate the code from using the `tabulate` library to the `rich` library:
1. **Import Change**: Removed the import of `tabulate` and replaced it with the necessary import from `rich.table` and `rich.console`.
2. **Table Creation**: Replaced the `tabulate` function with the `Table` class from `rich.table` to create the table.
3. **Console Output**: Used `Console` from `rich.console` to render the table.
4. **Output Type Handling**: The `tabulate` library supports multiple formats (e.g., `rst`, `github`), but `rich` does not have a direct equivalent for these formats. Instead, `rich` renders tables in a consistent, styled format. The `output_type` parameter is ignored in this migration since `rich` does not support multiple table formats.

### Modified Code
```python
"""Generate rST reports."""

from typing import Any, List

from rich.table import Table
from rich.console import Console

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

    # Create a rich Table
    table = Table(title="Test Report")

    # Add headers to the table
    headers = [
        "Environment",
        "Setup successful",
        "Passing tests",
        "Upgraded packages",
        "Lowered packages",
        "Package version",
    ]
    for header in headers:
        table.add_column(header)

    # Add rows to the table
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

    # Render the table using Console
    console = Console()
    console.print(table)

    # Return the table object for further use if needed
    return table
```

### Key Notes
- The `rich` library does not support output formats like `rst` or `github`. Instead, it provides a styled table output directly in the console. If the `output_type` parameter is critical for your application, additional logic would need to be implemented to handle it separately.
- The `Console.print` method is used to render the table to the console. The table object is also returned for potential further use.