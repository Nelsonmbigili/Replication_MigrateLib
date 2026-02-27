### Explanation of Changes
To migrate the code from using the `tabulate` library to the `prettytable` library:
1. Replaced the `tabulate` function with the `PrettyTable` class from `prettytable`.
2. Created a `PrettyTable` object and set the headers using the `field_names` attribute.
3. Added rows to the table using the `add_row` method.
4. Adjusted the output format to match the `output_type` parameter. The `prettytable` library uses `set_style` to define table styles, so I mapped the `rst` and `github` formats to their corresponding `prettytable` styles (`DEFAULT` and `MARKDOWN` respectively).
5. Returned the string representation of the `PrettyTable` object using its `get_string` method.

### Modified Code
```python
"""Generate rST reports."""

from typing import Any, List

from prettytable import PrettyTable, DEFAULT, MARKDOWN

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
    rows: List[List] = []
    for env in testers:
        upgraded = env.upgraded_packages()
        lowered = env.lowered_packages()
        for pkg in upgraded:
            rows.append(
                [
                    env.envname,
                    env.setup_status,
                    env.status,
                    pkg["name"],
                    "",
                    pkg["version"],
                ]
            )
        for pkg in lowered:
            rows.append(
                [
                    env.envname,
                    env.setup_status,
                    env.status,
                    "",
                    pkg["name"],
                    pkg["version"],
                ]
            )

    # Create a PrettyTable object and set headers
    table = PrettyTable()
    table.field_names = headers

    # Add rows to the table
    for row in rows:
        table.add_row(row)

    # Set the table style based on the output_type
    if output_type == "rst":
        table.set_style(DEFAULT)
    elif output_type == "github":
        table.set_style(MARKDOWN)

    # Return the table as a string
    return table.get_string()
```