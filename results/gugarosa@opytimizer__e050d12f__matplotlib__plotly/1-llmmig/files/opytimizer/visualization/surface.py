"""3-D benchmarking functions plots.
"""

import numpy as np
import plotly.graph_objects as go


def plot(
    points: np.ndarray,
    title: str = "",
    subtitle: str = "",
    style: str = "Viridis",
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

    # Create the surface plot
    surface = go.Surface(
        x=points[0],
        y=points[1],
        z=points[2],
        colorscale=style,
        showscale=colorbar,  # Show colorbar if enabled
    )

    # Create the wireframe plot (optional for visual effect)
    wireframe = go.Scatter3d(
        x=points[0].flatten(),
        y=points[1].flatten(),
        z=points[2].flatten(),
        mode="lines",
        line=dict(color="grey", width=1),
        showlegend=False,
    )

    # Create the figure
    fig = go.Figure(data=[surface, wireframe])

    # Update layout for titles, labels, and other settings
    fig.update_layout(
        scene=dict(
            xaxis_title="$x$",
            yaxis_title="$y$",
            zaxis_title="$f(x, y)$",
        ),
        title=dict(
            text=f"{title}<br><sub>{subtitle}</sub>",
            x=0.5,
            xanchor="center",
            font=dict(size=14),
        ),
    )

    # Render the plot
    fig.show()
