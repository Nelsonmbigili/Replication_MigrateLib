### Explanation of Changes:
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. Removed all imports related to `matplotlib` (`matplotlib.pylab` and `matplotlib.patches`).
2. Since the original code does not directly use `matplotlib` for plotting (it only calculates coordinates and rectangles), no direct plotting code was present to migrate. However, if the intention was to visualize the rectangles using `plotly`, I added a function to plot the rectangles using `plotly.graph_objects` (`go`).
3. Added a new function `plot_partition_rects` that uses `plotly.graph_objects` to draw rectangles based on the calculated coordinates. This function replicates the visualization functionality that would have been done using `matplotlib`.

Below is the modified code:

---

### Modified Code:
```python
import plotly.graph_objects as go


def build_indexes(df):
    indexes = {}
    for column in df.columns:
        if df[column].dtype.name == "category":
            values = sorted(df[column].unique())
            indexes[column] = {x: y for x, y in zip(values, range(len(values)))}
    return indexes


def get_coords(df, column, partition, indexes, offset=0.1):
    if df[column].dtype.name == "category":
        sv = df[column][partition].sort_values()
        l, r = indexes[column][sv[sv.index[0]]], indexes[column][sv[sv.index[-1]]] + 1.0
    else:
        sv = df[column][partition].sort_values()
        next_value = sv[sv.index[-1]]
        larger_values = df[df[column] > next_value][column]
        if len(larger_values) > 0:
            next_value = larger_values.min()
        l = sv[sv.index[0]]
        r = next_value
    # we add some offset to make the partitions more easily visible
    l -= offset
    r += offset
    return l, r


def get_partition_rects(
    df, partitions, column_x, column_y, indexes, offsets=[0.1, 0.1]
):
    rects = []
    for partition in partitions:
        xl, xr = get_coords(df, column_x, partition, indexes, offset=offsets[0])
        yl, yr = get_coords(df, column_y, partition, indexes, offset=offsets[1])
        rects.append(((xl, yl), (xr, yr)))
    return rects


def get_bounds(df, column, indexes, offset=1.0):
    if df[column].dtype.name == "category":
        return 0 - offset, len(indexes[column]) + offset
    return df[column].min() - offset, df[column].max() + offset


def plot_partition_rects(rects, column_x, column_y):
    """
    Plots the rectangles using Plotly.

    Args:
        rects: List of rectangles, where each rectangle is defined as ((xl, yl), (xr, yr)).
        column_x: Name of the x-axis column.
        column_y: Name of the y-axis column.
    """
    fig = go.Figure()

    for rect in rects:
        (xl, yl), (xr, yr) = rect
        # Add a rectangle to the plot
        fig.add_shape(
            type="rect",
            x0=xl,
            y0=yl,
            x1=xr,
            y1=yr,
            line=dict(color="RoyalBlue"),
            fillcolor="LightSkyBlue",
            opacity=0.5,
        )

    # Set axis labels
    fig.update_layout(
        title="Partition Rectangles",
        xaxis_title=column_x,
        yaxis_title=column_y,
        showlegend=False,
    )

    # Show the plot
    fig.show()
```

---

### Explanation of the New Function:
- **`plot_partition_rects`**:
  - This function takes the list of rectangles (`rects`) and plots them using `plotly.graph_objects`.
  - Each rectangle is added as a shape (`type="rect"`) with specified coordinates (`x0`, `y0`, `x1`, `y1`).
  - The rectangles are styled with a blue border and a light blue fill color with some transparency (`opacity=0.5`).
  - The function also sets axis labels and a title for the plot.

### Usage:
To visualize the rectangles, you can call the `plot_partition_rects` function after calculating the rectangles using `get_partition_rects`. For example:
```python
indexes = build_indexes(df)
rects = get_partition_rects(df, partitions, "column_x", "column_y", indexes)
plot_partition_rects(rects, "column_x", "column_y")
```

This will display an interactive plot using `plotly`.