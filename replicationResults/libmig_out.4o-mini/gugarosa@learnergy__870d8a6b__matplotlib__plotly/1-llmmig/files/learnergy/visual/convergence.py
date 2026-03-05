"""Convergence-related visualization.
"""

from typing import List, Optional

import plotly.graph_objects as go
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

    fig = go.Figure()

    if labels:
        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    for (arg, label) in zip(args, labels):
        fig.add_trace(go.Scatter(x=ticks, y=arg, mode='lines', name=label))

    fig.update_layout(
        title=dict(text=title, font=dict(size=14), x=0, xanchor='left'),
        titlefont=dict(size=8, color="grey"),
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        xaxis=dict(tickvals=ticks, range=[1, ticks[-1]]),
        showlegend=legend
    )

    fig.show()
