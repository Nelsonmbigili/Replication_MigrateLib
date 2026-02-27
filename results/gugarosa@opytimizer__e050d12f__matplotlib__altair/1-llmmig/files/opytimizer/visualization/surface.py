"""3-D benchmarking functions plots.
"""

import altair as alt
import pandas as pd
import numpy as np


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
    # Reshape the points into a tabular format for Altair
    x, y, z = points[0].ravel(), points[1].ravel(), points[2].ravel()
    data = pd.DataFrame({"x": x, "y": y, "z": z})

    # Create the Altair chart
    chart = (
        alt.Chart(data)
        .mark_point(filled=True, size=60)
        .encode(
            x=alt.X("x:Q", title="$x$"),
            y=alt.Y("y:Q", title="$y$"),
            color=alt.Color("z:Q", title="$f(x, y)$", scale=alt.Scale(scheme=style)),
            tooltip=["x", "y", "z"],  # Optional: Add tooltips for interactivity
        )
        .properties(
            title={
                "text": [title],
                "subtitle": [subtitle],
                "fontSize": 14,
                "subtitleFontSize": 10,
                "subtitleColor": "grey",
            },
            width=600,
            height=400,
        )
    )

    # Display the chart
    chart.show()
