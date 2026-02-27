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

    if labels:
        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    # Create a figure with seaborn styling
    sns.set_theme(style="whitegrid" if grid else "white")
    _, ax = sns.subplots(figsize=(7, 5))

    # Plot each variable using seaborn's lineplot
    for (arg, label) in zip(args, labels):
        sns.lineplot(x=ticks, y=arg, label=label, ax=ax)

    # Set axis labels and limits
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_xticks(ticks)
    ax.set_xlim(xmin=1, xmax=ticks[-1])

    # Set titles
    ax.set_title(title, loc="left", fontsize=14)
    ax.set_title(subtitle, loc="right", fontsize=8, color="grey")

    # Handle legend visibility
    if not legend:
        ax.legend_.remove()

    # Show the plot
    sns.plt.show()
