### Explanation of Changes
To migrate the code from using `matplotlib` to `plotly`, several key changes were made:

1. **Importing Plotly**: The import statement was changed from `matplotlib.pyplot` to `plotly.graph_objects` to utilize Plotly's graphing capabilities.
2. **Figure Creation**: Instead of creating a figure with `plt.figure()`, we now create a `plotly.graph_objects.Figure()`.
3. **3D Axes**: The 3D axes are handled differently in Plotly. We use `plotly.graph_objects.Surface` for the surface plot and `plotly.graph_objects.Scatter3d` for the wireframe.
4. **Setting Titles and Labels**: Titles and axis labels are set using the `update_layout` method in Plotly.
5. **Colorbar**: The colorbar is integrated into the surface plot in Plotly, so we don't need a separate call for it.
6. **Displaying the Plot**: Instead of `plt.show()`, we use `fig.show()` to display the plot.

### Modified Code
```python
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
```