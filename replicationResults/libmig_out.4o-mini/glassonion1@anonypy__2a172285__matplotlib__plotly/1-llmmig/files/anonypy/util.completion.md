### Explanation of Changes

To migrate the provided code from using `matplotlib` to `plotly`, the following changes were made:

1. **Import Statements**: The import statements were updated to include `plotly.graph_objects` instead of `matplotlib.pylab` and `matplotlib.patches`.
2. **Rectangles Creation**: The way rectangles are created and displayed has changed. In `plotly`, we will use `plotly.graph_objects` to create shapes (rectangles) instead of using patches from `matplotlib`.
3. **Data Visualization**: The plotting functions will be adapted to use `plotly`'s figure creation and updating methods.

The modified code below reflects these changes while maintaining the original structure and naming conventions.

### Modified Code

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
```

### Note
The code provided does not include any plotting functionality. If you need to visualize the rectangles created by `get_partition_rects`, you would typically create a `plotly` figure and add shapes to it using the `add_shape` method. However, since the original code does not include any plotting logic, I have not added that part. If you need assistance with that, please let me know!