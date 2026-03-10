"""Convergence plots.
"""

from typing import List, Optional
import altair as alt
import pandas as pd

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

    # Prepare data for Altair
    data = pd.DataFrame({f'variable_{i}': arg for i, arg in enumerate(args)})
    data['iteration'] = data.index

    # Create the base chart
    base = alt.Chart(data).transform_fold(
        [f'variable_{i}' for i in range(len(args))],
        as_=['variable', 'value']
    ).mark_line().encode(
        x='iteration:Q',
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

    # Display the chart
    base.display()
