"""3-D benchmarking functions plots.
"""

import altair as alt
import numpy as np
import pandas as pd


def plot(
    points: np.ndarray,
    title: str = "",
    subtitle: str = "",
    style: str = "winter",
    colorbar: bool = True,
) -> None:
    """Plots the surface from a 3-dimensional function.

    Args:
        points: Points to be plotted with shape equal to (3, n, n).
        title: Title of the plot.
        subtitle: Subtitle of the plot.
        style: Surface's style.
        colorbar: If colorbar should be used or not.

    """
    
    # Prepare data for Altair
    x = points[0].flatten()
    y = points[1].flatten()
    z = points[2].flatten()
    data = pd.DataFrame({'x': x, 'y': y, 'z': z})

    # Create the surface plot
    surface = alt.Chart(data).mark_rect().encode(
        x='x:Q',
        y='y:Q',
        color=alt.Color('z:Q', scale=alt.Scale(scheme=style))
    ).properties(
        title=title
    )

    # Create the wireframe plot
    wireframe = alt.Chart(data).mark_line(color='grey').encode(
        x='x:Q',
        y='y:Q'
    ).transform_filter(
        alt.datum.z == alt.datum.z  # This is a placeholder for wireframe logic
    )

    # Combine the surface and wireframe
    chart = surface + wireframe

    # Display the chart
    chart.properties(
        width=600,
        height=300
    ).configure_title(
        fontSize=14
    ).configure_axis(
        labelFontSize=8
    ).show()
