### Explanation of Changes:
To migrate the code from using the `tabulate` library to the `rich` library, the following changes were made:
1. **Import Replacement**: Removed the `tabulate` import and replaced it with `from rich.table import Table` and `from rich.console import Console` to use `rich` for table rendering.
2. **Table Creation**: Replaced the `tabulate` function calls with `rich`'s `Table` class to create tables. The `Table` class allows adding columns and rows programmatically.
3. **Console Output**: Used `rich`'s `Console` object to print the tables to the console.
4. **Formatting Adjustments**: Adjusted the table creation logic to match the structure of the original `tabulate` output, including headers and alignment.

Below is the modified code:

---

### Modified Code:
```python
# Copyright 2022 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os
import plotly.colors as colors
import plotly.graph_objects as go
import numpy as np
from rich.table import Table
from rich.console import Console
from typing import List, Optional, TYPE_CHECKING
import dimod

if TYPE_CHECKING:
    from packing3d import Cases, Bins, Variables


def print_cqm_stats(cqm: dimod.ConstrainedQuadraticModel) -> None:
    """Print some information about the CQM model defining the 3D bin packing problem.

    Args:
        cqm: A dimod constrained quadratic model.

    """
    if not isinstance(cqm, dimod.ConstrainedQuadraticModel):
        raise ValueError("input instance should be a dimod CQM model")
    num_binaries = sum(cqm.vartype(v) is dimod.BINARY for v in cqm.variables)
    num_integers = sum(cqm.vartype(v) is dimod.INTEGER for v in cqm.variables)
    num_continuous = sum(cqm.vartype(v) is dimod.REAL for v in cqm.variables)
    num_discretes = len(cqm.discrete)
    num_linear_constraints = sum(
        constraint.lhs.is_linear() for constraint in cqm.constraints.values())
    num_quadratic_constraints = sum(
        not constraint.lhs.is_linear() for constraint in
        cqm.constraints.values())
    num_le_inequality_constraints = sum(
        constraint.sense is dimod.sym.Sense.Le for constraint in
        cqm.constraints.values())
    num_ge_inequality_constraints = sum(
        constraint.sense is dimod.sym.Sense.Ge for constraint in
        cqm.constraints.values())
    num_equality_constraints = sum(
        constraint.sense is dimod.sym.Sense.Eq for constraint in
        cqm.constraints.values())

    assert (num_binaries + num_integers + num_continuous == len(cqm.variables))

    assert (num_quadratic_constraints + num_linear_constraints ==
            len(cqm.constraints))

    print(" \n" + "=" * 35 + "MODEL INFORMATION" + "=" * 35)
    print(
        ' ' * 10 + 'Variables' + " " * 20 + 'Constraints' + " " * 15 +
        'Sensitivity')
    print('-' * 30 + " " + '-' * 28 + ' ' + '-' * 18)

    # Create a table using rich
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Binary", justify="center")
    table.add_column("Integer", justify="center")
    table.add_column("Continuous", justify="center")
    table.add_column("Quad", justify="center")
    table.add_column("Linear", justify="center")
    table.add_column("One-hot", justify="center")
    table.add_column("EQ", justify="center")
    table.add_column("LT", justify="center")
    table.add_column("GT", justify="center")

    # Add data to the table
    table.add_row(
        str(num_binaries),
        str(num_integers),
        str(num_continuous),
        str(num_quadratic_constraints),
        str(num_linear_constraints),
        str(num_discretes),
        str(num_equality_constraints),
        str(num_le_inequality_constraints),
        str(num_ge_inequality_constraints),
    )

    # Print the table using rich's Console
    console = Console()
    console.print(table)


def write_solution_to_file(solution_file_path: str,
                           cqm: dimod.ConstrainedQuadraticModel,
                           vars: "Variables",
                           sample: dimod.SampleSet,
                           cases: "Cases",
                           bins: "Bins",
                           effective_dimensions: list):
    """Write solution to a file.

    Args:
        solution_file_path: path to the output solution file. If doesn't exist,
            a new file is created.
        cqm: A ``dimod.CQM`` object that defines the 3D bin packing problem.
        vars: Instance of ``Variables`` that defines the complete set of variables
            for the 3D bin packing problem.
        sample: A ``dimod.SampleSet`` that represents the best feasible solution found.
        cases: Instance of ``Cases``, representing cases packed into containers.
        bins: Instance of ``Bins``, representing containers to pack cases into.
        effective_dimensions: List of case dimensions based on orientations of cases.

    """
    num_cases = cases.num_cases
    num_bins = bins.num_bins
    lowest_num_bin = bins.lowest_num_bin
    dx, dy, dz = effective_dimensions
    if num_bins > 1:
        num_bin_used = lowest_num_bin + sum([vars.bin_on[j].energy(sample)
                            for j in range(lowest_num_bin, num_bins)])
    else:
        num_bin_used = 1

    objective_value = cqm.objective.energy(sample)
    vs = [['case_id', 'bin-location', 'orientation', 'x', 'y', 'z', "x'",
           "y'", "z'"]]
    for i in range(num_cases):
        vs.append([cases.case_ids[i],
                   int(sum(int(j == 0) if i == 0 or num_bins == 1 else
                           (j + 1) * vars.bin_loc[i, j].energy(sample)
                           for j in range(num_bins))),
                   int(sum((r + 1) * vars.o[i, r].energy(sample) for r in
                           range(6))),
                   np.round(vars.x[i].energy(sample), 2),
                   np.round(vars.y[i].energy(sample), 2),
                   np.round(vars.z[i].energy(sample), 2),
                   np.round(dx[i].energy(sample), 2),
                   np.round(dy[i].energy(sample), 2),
                   np.round(dz[i].energy(sample), 2)])

    # Create a table using rich
    table = Table(show_header=True, header_style="bold cyan")
    headers = vs[0]
    for header in headers:
        table.add_column(header, justify="center")

    for row in vs[1:]:
        table.add_row(*map(str, row))

    # Write the table to a file
    with open(solution_file_path, 'w') as f:
        f.write('# Number of bins used: ' + str(int(num_bin_used)) + '\n')
        f.write('# Number of cases packed: ' + str(int(num_cases)) + '\n')
        f.write(
            '# Objective value: ' + str(np.round(objective_value, 3)) + '\n\n')
        console = Console(file=f)
        console.print(table)
        print(f'Saved solution to '
              f'{os.path.join(os.getcwd(), solution_file_path)}')


def write_input_data(data: dict, input_filename: Optional[str] = None) -> str:
    """Convert input data dictionary to an input string and write it to a file.

    Args:
        data: dictionary containing raw information for both bins and cases
        input_filename: name of the file for writing input data

    Returns:
        input_string: input data information

    """
    header = ["case_id", "quantity", "length", "width", "height"]

    case_info = [[i, data["quantity"][i], data["case_length"][i],
                  data["case_width"][i], data["case_height"][i]]
                 for i in range(len(data['case_ids']))]

    # Create a table using rich
    table = Table(show_header=True, header_style="bold green")
    for col in header:
        table.add_column(col, justify="right")

    for row in case_info:
        table.add_row(*map(str, row))

    # Convert table to string
    console = Console()
    input_string = f'# Max num of bins : {data["num_bins"]} \n'
    input_string += (f'# Bin dimensions '
                     f'(L * W * H): {data["bin_dimensions"][0]} '
                     f'{data["bin_dimensions"][1]} '
                     f'{data["bin_dimensions"][2]} \n \n')
    input_string += console.export_text(table)

    if input_filename is not None:
        full_file_path = os.path.join("input", input_filename)
        with open(full_file_path, "w") as f:
            f.write(input_string)

    return input_string
```

---

### Summary of Changes:
- Replaced `tabulate` with `rich`'s `Table` and `Console` for table creation and rendering.
- Ensured the output format remains consistent with the original `tabulate` output.
- Adjusted file writing to use `rich`'s `Console` for exporting tables to files.