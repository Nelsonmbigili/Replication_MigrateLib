"""Convergence plots.
"""

from typing import List, Optional

import plotly.graph_objects as go

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

    if labels:
        if not isinstance(labels, list):
            raise e.TypeError("`labels` should be a list")

        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    # Create a plotly figure
    fig = go.Figure()

    # Add traces for each variable
    for (arg, label) in zip(args, labels):
        fig.add_trace(go.Scatter(y=arg, mode="lines", name=label))

    # Update layout with titles, labels, and grid
    fig.update_layout(
        title={
            "text": f"{title}<br><sub>{subtitle}</sub>",
            "x": 0.01,
            "xanchor": "left",
        },
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        showlegend=legend,
        xaxis=dict(showgrid=grid),
        yaxis=dict(showgrid=grid),
    )

    # Show the plot
    fig.show()
