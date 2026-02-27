The following Python code currently uses the library "tabulate" version 0.9.0.
Migrate this code to use the library "rich" version 14.0.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "tabulate" to "rich".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "tabulate" and "rich".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""Generate rST reports."""

from typing import Any, List

from tabulate import tabulate

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

    return tabulate(rows, headers=headers, tablefmt=output_type)

```