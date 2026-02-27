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
indexes = build_indexes(df)
rects = get_partition_rects(df, partitions, "column_x", "column_y", indexes)
plot_partition_rects(rects, "column_x", "column_y")
