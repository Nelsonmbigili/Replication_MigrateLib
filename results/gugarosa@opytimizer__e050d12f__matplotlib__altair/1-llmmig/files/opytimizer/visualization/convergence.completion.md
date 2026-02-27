### Explanation of Changes
To migrate the code from `matplotlib` to `altair`, the following changes were made:
1. **Import Changes**: Removed the `matplotlib.pyplot` import and replaced it with `altair` import.
2. **Plotting Logic**: `altair` uses a declarative approach to create visualizations. Instead of directly plotting on axes, data is structured into a `pandas.DataFrame`, and the plot is defined using `alt.Chart`.
3. **Grid and Legend**: In `altair`, gridlines and legends are handled through chart configuration and encoding options.
4. **Dynamic Labels**: Labels are added as a column in the `DataFrame` to allow `altair` to group and color the lines accordingly.
5. **Title and Subtitle**: `altair` supports titles directly in the chart configuration, so these were added using the `properties` method.
6. **Display**: Instead of `plt.show()`, `altair` charts are displayed directly in supported environments (e.g., Jupyter Notebook) or saved to files.

### Modified Code
```python
"""Convergence plots.
"""

from typing import List, Optional

import pandas as pd
import altair as alt

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

    if labels:
        if not isinstance(labels, list):
            raise e.TypeError("`labels` should be a list")

        if len(labels) != len(args):
            raise e.SizeError("`args` and `labels` should have the same size")
    else:
        labels = [f"variable_{i}" for i in range(len(args))]

    # Prepare data for Altair
    data = []
    for i, arg in enumerate(args):
        data.extend({"iteration": j, "value": val, "label": labels[i]} for j, val in enumerate(arg))

    df = pd.DataFrame(data)

    # Create the Altair chart
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("iteration:Q", title=xlabel),
            y=alt.Y("value:Q", title=ylabel),
            color=alt.Color("label:N", title="Legend" if legend else None),
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
    if not grid:
        chart = chart.configure_axis(grid=False)

    # Display the chart
    chart.display()
```

### Key Notes
- The `altair` chart is built using a `pandas.DataFrame` to structure the data, which is required for `altair`'s declarative syntax.
- The `grid` and `legend` options are handled through `altair`'s configuration and encoding.
- The `chart.display()` method is used to render the chart in supported environments. If running in a script, you may need to save the chart using `chart.save('output.html')` and open it in a browser.