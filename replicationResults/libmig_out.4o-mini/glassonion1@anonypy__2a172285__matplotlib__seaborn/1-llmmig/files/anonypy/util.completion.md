### Explanation of Changes
To migrate the code from using `matplotlib` to `seaborn`, I made the following changes:

1. **Import Statement**: Removed the import of `matplotlib.pylab` and `matplotlib.patches` since they are not needed in the `seaborn` context.
2. **Data Visualization**: The original code does not include any visualization functions, but if it were to visualize data, we would typically use `seaborn` functions like `sns.scatterplot`, `sns.lineplot`, etc., instead of `matplotlib` plotting functions. However, since the provided code does not include any plotting, no specific visualization changes were made.
3. **Data Handling**: The logic for handling data remains the same, as both libraries can work with pandas DataFrames. The code primarily focuses on data manipulation rather than visualization.

Since the original code does not include any plotting or visualization, the migration mainly involves removing unnecessary imports. The core functionality remains unchanged.

### Modified Code
```python
import pandas as pd  # Assuming pandas is used for DataFrame handling
import seaborn as sns  # Importing seaborn instead of matplotlib

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

In this modified code, the import statement for `matplotlib` has been replaced with `seaborn`, but since the original code does not perform any plotting, no further changes were necessary.