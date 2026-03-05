"""3-D benchmarking functions plots.
"""

import plotly.graph_objects as go
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

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=points[0].flatten(),
        y=points[1].flatten(),
        z=points[2].flatten(),
        mode='lines',
        line=dict(color='grey', width=0.5),
        name='Wireframe'
    ))

    fig.add_trace(go.Surface(
        z=points[2],
        x=points[0],
        y=points[1],
        colorscale=style,
        showscale=colorbar,
        colorbar=dict(thickness=15, title="Colorbar", titleside="right")
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=14), x=0, xanchor='left'),
        titlefont=dict(size=8, color="grey"),
        scene=dict(
            xaxis_title="$x$",
            yaxis_title="$y$",
            zaxis_title="$f(x, y)$"
        ),
        width=900,
        height=500
    )

    fig.show()
