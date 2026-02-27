"""Convergence-related visualization.
"""

from typing import List, Optional

import altair as alt
import pandas as pd
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

    # Prepare data for Altair
    data = []
    for tick, values in zip(ticks, zip(*args)):
        for label, value in zip(labels, values):
            data.append({"epoch": tick, "label": label, "value": value})

    df = pd.DataFrame(data)

    # Create the Altair chart
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("epoch:Q", title=xlabel),
            y=alt.Y("value:Q", title=ylabel),
            color=alt.Color("label:N", legend=alt.Legend(title="Legend") if legend else None),
        )
        .properties(
            title={
                "text": title,
                "subtitle": subtitle,
                "fontSize": 14,
                "subtitleFontSize": 10,
                "subtitleColor": "grey",
            },
            width=700,
            height=500,
        )
    )

    # Add gridlines if required
    if grid:
        chart = chart.configure_axis(grid=True)

    # Display the chart
    chart.display()