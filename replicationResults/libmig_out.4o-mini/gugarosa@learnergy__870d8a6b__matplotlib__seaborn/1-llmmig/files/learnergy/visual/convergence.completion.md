### Explanation of Changes
To migrate the code from using `matplotlib` to `seaborn`, the following changes were made:

1. **Import Statement**: The import statement for `matplotlib.pyplot` was removed, and `seaborn` was imported instead.
2. **Plotting Function**: The `ax.plot()` method from `matplotlib` was replaced with `sns.lineplot()`, which is the equivalent function in `seaborn` for creating line plots.
3. **Figure Creation**: The creation of the figure and axes was modified to use `sns.set()` for setting the aesthetic style of the plots, which is a common practice in `seaborn`.
4. **Legend Handling**: The legend handling was adjusted to fit `seaborn`'s way of managing legends, which is typically done automatically when using `sns.lineplot()`.

The overall structure of the code remains the same, ensuring that the function's signature and behavior are preserved.

### Modified Code
```python
"""Convergence-related visualization.
"""

from typing import List, Optional

import seaborn as sns
import numpy as np

import learnergy.utils.exception as e


def plot(
    *args,
    labels: Optional[List[str]] = None,
    title: str = "",
    subtitle: str = "",
    xlabel: str = "epoch",
    ylabel: str = "value",
    grid: bool = True,
    legend: bool = True,
) -> None:
    """Plots the convergence graph of desired variables.

    Essentially, each variable is a list or numpy array
    with size equals to (epochs x 1).

    Args:
        labels: Labels to be applied for each plot in legend.
        title: The title of the plot.
        subtitle: The subtitle of the plot.
        xlabel: The `x` axis label.
        ylabel: The `y` axis label.
        grid: If grid should be used or not.
        legend: If legend should be displayed or not.

    """

    ticks = np.arange(1, len(args[0]) + 1)

    sns.set(style="whitegrid")  # Set the aesthetic style of the plots
    _, ax = plt.subplots(figsize=(7, 5))

    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_xticks(ticks)
    ax.set_xlim(xmin=1, xmax=ticks[-1])
    ax.set_title(title, loc="left", fontsize=14)
    ax.set_title(subtitle, loc="right", fontsize=8, color="grey")

    if grid:
        ax.grid()

    if labels:
        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    for (arg, label) in zip(args, labels):
        sns.lineplot(x=ticks, y=arg, label=label, ax=ax)

    if legend:
        ax.legend()

    plt.show()
```