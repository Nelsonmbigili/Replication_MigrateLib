The following Python code currently uses the library "matplotlib" version 3.10.1.
Migrate this code to use the library "seaborn" version 0.13.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "matplotlib" to "seaborn".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "matplotlib" and "seaborn".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""Convergence plots.
"""

from typing import List, Optional

import matplotlib.pyplot as plt

import opytimizer.utils.exception as e


def plot(
    *args,
    labels: Optional[List[str]] = None,
    title: str = "",
    subtitle: str = "",
    xlabel: str = "iteration",
    ylabel: str = "value",
    grid: bool = True,
    legend: bool = True,
) -> None:
    """Plots the convergence graph of desired variables.

    Essentially, each variable is a list or numpy array
    with size equals to `n_iterations`.

    Args:
        labels: Labels to be applied for each plot in legend.
        title: Title of the plot.
        subtitle: Subtitle of the plot.
        xlabel: Axis `x` label.
        ylabel: Axis `y` label.
        grid: If grid should be used or not.
        legend: If legend should be displayed or not.

    """

    _, ax = plt.subplots(figsize=(7, 5))

    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_title(title, loc="left", fontsize=14)
    ax.set_title(subtitle, loc="right", fontsize=8, color="grey")

    if grid:
        ax.grid()

    if labels:
        if not isinstance(labels, list):
            raise e.TypeError("`labels` should be a list")

        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    for (arg, label) in zip(args, labels):
        ax.plot(arg, label=label)

    if legend:
        ax.legend()

    plt.show()

```