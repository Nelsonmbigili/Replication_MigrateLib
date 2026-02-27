The following Python code currently uses the library "matplotlib" version 3.10.1.
Migrate this code to use the library "plotly" version 6.0.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "matplotlib" to "plotly".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "matplotlib" and "plotly".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""3-D benchmarking functions plots.
"""

import matplotlib.pyplot as plt
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

    fig = plt.figure(figsize=(9, 5))
    ax = plt.axes(projection="3d")

    ax.set(xlabel="$x$", ylabel="$y$", zlabel="$f(x, y)$")
    ax.set_title(title, loc="left", fontsize=14)
    ax.set_title(subtitle, loc="right", fontsize=8, color="grey")
    ax.tick_params(labelsize=8)

    ax.plot_wireframe(points[0], points[1], points[2], color="grey")
    surface = ax.plot_surface(
        points[0],
        points[1],
        points[2],
        rstride=1,
        cstride=1,
        cmap=style,
        edgecolor="none",
    )

    if colorbar:
        fig.colorbar(surface, shrink=0.5, aspect=10)

    plt.show()

```