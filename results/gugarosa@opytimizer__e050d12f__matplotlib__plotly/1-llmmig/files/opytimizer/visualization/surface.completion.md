### Explanation of Changes:
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. Replaced `matplotlib.pyplot` and its 3D plotting functions with `plotly.graph_objects` (commonly abbreviated as `go`).
2. Used `go.Surface` to create the 3D surface plot, which replaces `ax.plot_surface`.
3. Used `go.Figure` to create the figure and add the surface plot to it.
4. Added a color scale using `colorscale` in `go.Surface` to replace the `cmap` argument in `matplotlib`.
5. Added a color bar using `colorbar` in `go.Surface` instead of `fig.colorbar`.
6. Replaced `ax.plot_wireframe` with `go.Scatter3d` to create a wireframe-like effect.
7. Adjusted the title and subtitle using `update_layout` in `plotly`.
8. Removed `plt.show()` since `plotly` figures are rendered interactively in supported environments.

### Modified Code:
```python
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
```

### Key Notes:
- The `style` parameter now maps to `colorscale` in `plotly`. Common options include "Viridis", "Cividis", "Plasma", etc.
- The `colorbar` parameter directly controls whether the color scale is displayed.
- The `go.Scatter3d` is used to mimic the wireframe effect, as `plotly` does not have a direct equivalent of `ax.plot_wireframe`.
- The `fig.update_layout` method is used to set axis labels and titles, including the subtitle.

This code should now work seamlessly with `plotly` version 6.0.1.