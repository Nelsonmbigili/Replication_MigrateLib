"""Convergence plots.
"""

from typing import List, Optional

import seaborn as sns
import matplotlib.pyplot as plt  # Required for subtitle handling

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

    # Set Seaborn theme
    sns.set_theme(style="whitegrid" if grid else "white")

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(7, 5))

    # Validate labels
    if labels:
        if not isinstance(labels, list):
            raise e.TypeError("`labels` should be a list")

        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    # Plot each variable using Seaborn's lineplot
    for (arg, label) in zip(args, labels):
        sns.lineplot(x=range(len(arg)), y=arg, label=label, ax=ax)

    # Set axis labels
    ax.set(xlabel=xlabel, ylabel=ylabel)

    # Set title and subtitle
    ax.set_title(title, loc="left", fontsize=14)
    ax.set_title(subtitle, loc="right", fontsize=8, color="grey")

    # Handle legend
    if not legend:
        ax.legend_.remove()

    # Show the plot
    plt.show()
