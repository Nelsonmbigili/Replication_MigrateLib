### Explanation of Changes
To migrate the code from `matplotlib` to `altair`, the following changes were made:
1. **Removed `matplotlib` imports**: The `matplotlib.pyplot` and related calls were replaced with `altair` equivalents.
2. **Replaced `plt.subplots` and axis configuration**: In `altair`, we use a declarative approach to define the chart, so axis labels, titles, and gridlines are set using chart properties.
3. **Replaced `ax.plot` with `altair.Chart`**: Instead of plotting directly on axes, `altair` requires data to be in a tabular format (e.g., pandas DataFrame). The input data was transformed into a DataFrame for plotting.
4. **Handled multiple lines**: `altair` supports layered charts for multiple lines. Each variable was assigned a label, and the data was reshaped to a long format for plotting.
5. **Legend and grid**: These are configured using `altair`'s chart properties.
6. **Removed `plt.show()`**: In `altair`, the chart is returned and displayed automatically in supported environments.

### Modified Code
Here is the complete code after migration to `altair`:

```python
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

    if labels:
        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    # Prepare data for Altair
    data = []
    for tick, values in zip(ticks, zip(*args)):
        for label, value in zip(labels, values):
            data.append({"epoch": tick, "label": label, "value": value})

    df = pd.DataFrame(data)

    # Create the Altair chart
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("epoch:Q", title=xlabel),
            y=alt.Y("value:Q", title=ylabel),
            color=alt.Color("label:N", legend=alt.Legend(title="Legend") if legend else None),
        )
        .properties(
            title={
                "text": title,
                "subtitle": subtitle,
                "fontSize": 14,
                "subtitleFontSize": 10,
                "subtitleColor": "grey",
            },
            width=700,
            height=500,
        )
    )

    # Add gridlines if required
    if grid:
        chart = chart.configure_axis(grid=True)

    # Display the chart
    chart.display()
```

### Key Notes
1. **Data Transformation**: `altair` requires data in a tabular format. The `args` input was transformed into a long-format DataFrame with columns `epoch`, `label`, and `value`.
2. **Chart Configuration**: Titles, subtitles, axis labels, and legend are configured using `altair`'s `properties` and `encode` methods.
3. **Gridlines**: Configured using `configure_axis(grid=True)`.
4. **Legend**: Controlled via the `color` encoding and `alt.Legend`.

This code should now work seamlessly with `altair` version 5.5.0.