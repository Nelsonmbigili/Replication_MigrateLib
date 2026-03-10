### Explanation of Changes
To migrate the code from using the `tabulate` library to the `prettytable` library, the following changes were made:

1. **Import Statement**: The import statement for `tabulate` was replaced with an import statement for `PrettyTable` from the `prettytable` library.
2. **Table Creation**: Instead of using the `tabulate` function to create the table, an instance of `PrettyTable` was created. The headers were set using the `field_names` attribute of the `PrettyTable` instance.
3. **Row Insertion**: Rows were added to the `PrettyTable` instance using the `add_row` method instead of appending to a list.
4. **Output Format**: The output format is handled by calling the `get_string` method of the `PrettyTable` instance, which generates the string representation of the table.

Here is the modified code:

```python
"""Generate rST reports."""

from typing import Any, List

from prettytable import PrettyTable

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

    table = PrettyTable()
    table.field_names = headers
    for row in rows:
        table.add_row(row)

    return table.get_string(format=output_type)
```