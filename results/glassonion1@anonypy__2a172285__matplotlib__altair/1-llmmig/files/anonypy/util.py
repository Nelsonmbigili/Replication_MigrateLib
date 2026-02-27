import altair as alt
import pandas as pd


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


def visualize_partitions(df, partitions, column_x, column_y, indexes, offsets=[0.1, 0.1]):
    """
    Visualize the partition rectangles using Altair.
    """
    rects = get_partition_rects(df, partitions, column_x, column_y, indexes, offsets)

    # Create a DataFrame for the rectangles
    rects_data = []
    for i, ((xl, yl), (xr, yr)) in enumerate(rects):
        rects_data.append({"x": xl, "y": yl, "x2": xr, "y2": yr, "partition": i})

    rects_df = pd.DataFrame(rects_data)

    # Create an Altair chart
    chart = alt.Chart(rects_df).mark_rect().encode(
        x=alt.X("x:Q", title=column_x),
        x2="x2:Q",
        y=alt.Y("y:Q", title=column_y),
        y2="y2:Q",
        color=alt.Color("partition:N", legend=None),  # Color by partition
    ).properties(
        width=600,
        height=400,
        title="Partition Rectangles"
    )

    return chart
# Example DataFrame
data = {
    "column_x": [1, 2, 3, 4, 5],
    "column_y": [5, 4, 3, 2, 1],
    "category": ["A", "B", "A", "B", "A"]
}
df = pd.DataFrame(data)
df["category"] = df["category"].astype("category")

# Build indexes
indexes = build_indexes(df)

# Define partitions (example: list of boolean masks)
partitions = [df.index[df["category"] == "A"], df.index[df["category"] == "B"]]

# Visualize
chart = visualize_partitions(df, partitions, "column_x", "column_y", indexes)
chart.show()
