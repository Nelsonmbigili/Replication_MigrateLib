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

    # Create a Plotly figure
    fig = go.Figure()

    if labels:
        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    # Add traces for each variable
    for (arg, label) in zip(args, labels):
        fig.add_trace(go.Scatter(x=ticks, y=arg, mode="lines", name=label))

    # Update layout with titles, labels, and grid
    fig.update_layout(
        title={
            "text": f"{title}<br><sup>{subtitle}</sup>",
            "x": 0.01,
            "xanchor": "left",
        },
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        showlegend=legend,
        font=dict(size=14),
    )

    # Configure x-axis ticks and limits
    fig.update_xaxes(
        tickmode="array",
        tickvals=ticks,
        range=[1, ticks[-1]],
    )

    # Configure grid visibility
    fig.update_layout(
        xaxis=dict(showgrid=grid),
        yaxis=dict(showgrid=grid),
    )

    # Show the figure
    fig.show()
