### Explanation of Changes:
To migrate the code from `matplotlib` to `seaborn`, the following changes were made:
1. **Removed `matplotlib` imports**: The original code imports `matplotlib.pylab` and `matplotlib.patches`, which are not needed when using `seaborn`.
2. **Replaced `matplotlib.patches.Rectangle` with `seaborn`'s plotting functions**: Instead of manually creating rectangles using `matplotlib.patches.Rectangle`, `seaborn` provides higher-level APIs for visualizing data. However, since the provided code does not include the actual plotting logic, no direct replacement for `Rectangle` is required in this snippet.
3. **No plotting logic in the provided code**: The provided code does not include any actual plotting or visualization logic. It primarily computes coordinates and bounds for partitions. Therefore, no further changes are necessary to migrate to `seaborn`.

Since the provided code does not directly use `matplotlib` for plotting, the migration to `seaborn` does not require any functional changes. The code remains the same, but the unused `matplotlib` imports are removed.

---

### Modified Code:
```python
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

---

### Key Notes:
- The provided code does not include any actual plotting logic, so no `seaborn` functions are introduced in this snippet.
- If the larger application includes plotting logic elsewhere, you would need to replace `matplotlib` plotting calls (e.g., `pl.plot`, `pl.scatter`, etc.) with equivalent `seaborn` functions (e.g., `sns.lineplot`, `sns.scatterplot`, etc.).
- The unused `matplotlib` imports were removed to clean up the code.