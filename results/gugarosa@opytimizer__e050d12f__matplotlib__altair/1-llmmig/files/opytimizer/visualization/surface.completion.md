### Explanation of Changes:
To migrate the code from `matplotlib` to `altair`, the following changes were made:
1. **Altair Import**: Replaced the `matplotlib` import with `altair` and removed the `matplotlib`-specific imports.
2. **Data Preparation**: Altair requires data in a tabular format (e.g., pandas DataFrame). The 3D points array was reshaped and converted into a DataFrame.
3. **Altair Chart**: Used `altair.Chart` with `mark_point` and `encode` to create a 3D scatter plot. Note that Altair does not natively support 3D plots, so the visualization is adapted to a 2D scatter plot with color encoding for the third dimension (`z`).
4. **Color Encoding**: Used Altair's `color` encoding to represent the `z` values (function output) with a color gradient.
5. **Titles and Labels**: Added titles and axis labels using Altair's `properties` and `encode` methods.
6. **Color Scheme**: Used Altair's `scale` to apply a color scheme similar to the `matplotlib` colormap.

### Modified Code:
```python
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
```

### Key Notes:
1. **3D Plot Limitation**: Altair does not natively support 3D plots. The visualization was adapted to a 2D scatter plot with color encoding for the `z` dimension.
2. **Color Scheme**: The `style` parameter is mapped to Altair's `scale` schemes. You may need to adjust the scheme name to match Altair's supported color schemes.
3. **Interactivity**: Altair charts are interactive by default. Tooltips were added to display the `x`, `y`, and `z` values on hover.
4. **Colorbar**: Altair does not have a separate colorbar toggle. The color gradient is always displayed in the legend.

This code provides a functional equivalent of the original `matplotlib` plot using `altair`.