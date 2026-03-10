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
    data = pd.DataFrame({f'variable_{i}': arg for i, arg in enumerate(args)})
    data['epoch'] = ticks

    if labels:
        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    # Melt the DataFrame to long format for Altair
    data = data.melt(id_vars='epoch', var_name='variable', value_name='value')

    chart = alt.Chart(data).mark_line().encode(
        x='epoch:Q',
        y='value:Q',
        color='variable:N'
    ).properties(
        title={
            "text": [title, subtitle],
            "subtitle": [subtitle],
            "anchor": "start"
        },
        width=700,
        height=500
    )

    chart.display()
