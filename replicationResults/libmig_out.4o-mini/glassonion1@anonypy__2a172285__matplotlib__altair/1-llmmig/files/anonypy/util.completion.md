### Explanation of Changes

To migrate the provided code from using `matplotlib` to `altair`, the following changes were made:

1. **Import Statements**: Removed the import of `matplotlib.pylab` and `matplotlib.patches` since they are not needed in `altair`.
2. **Data Visualization**: The original code does not include any visualization code, but if it were to visualize the rectangles created by `get_partition_rects`, we would use `altair`'s `mark_rect()` to create rectangles based on the coordinates calculated.
3. **Data Handling**: The logic for calculating coordinates and bounds remains unchanged, as it is independent of the visualization library. However, if visualization were to be added, we would need to create a `Chart` object in `altair` using the data processed by these functions.

Since the original code does not include any visualization logic, the migration focuses on ensuring that the data processing functions remain intact and ready for potential visualization with `altair`.

### Modified Code

```python
import altair as alt


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
```

This modified code retains the original functionality while preparing for potential integration with `altair` for visualization purposes.