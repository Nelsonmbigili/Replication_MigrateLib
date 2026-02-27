### Explanation of Changes
The migration from `seaborn` to `altair` involves the following changes:
1. **Heatmap (`sns.heatmap`)**: Altair does not have a direct heatmap function like Seaborn. Instead, we use a `mark_rect` plot with color encoding to create a heatmap.
2. **KDE Plot (`sns.kdeplot`)**: Altair does not have a built-in KDE plot. However, we can approximate it by using a density transform (`transform_density`) and plotting the result with `mark_line`.
3. **General Plotting (`ax.plot`)**: Altair uses a declarative approach to create line charts. We replace `ax.plot` with `alt.Chart` and use `mark_line` for line plots.

### Modified Code
Below is the modified code using `altair` version 5.5.0:

```python
import altair as alt
import pandas as pd
from collections import defaultdict
from ash_model.measures import *


def __rolling_mean(it, window):
    """
    :param it:
    :param window:
    :return:
    """
    return pd.Series(it).rolling(window=window).mean()


def plot_structure_dynamics(
    h: ASH, func: Callable, func_params: dict = None, rolling: int = None, **kwargs
) -> alt.Chart:
    """
    :param h: ASH instance
    :param func: function to be called at each timestamp
    :param func_params: parameters of the above function in key-value pairs
    :param rolling: size of the rolling window
    :param kwargs: Additional keyword arguments (not used in Altair)
    :return: Altair Chart object
    """
    if func_params is None:
        func_params = {}

    if "h" in func.__code__.co_varnames:  # e.g., inclusiveness
        func_params.update({"h": h})

    if "tid" in func.__code__.co_varnames:
        y = [
            func(**func_params, tid=tid) for tid in h.temporal_snapshots_ids()
        ]  # e.g., inclusiveness
    else:  # has 'start' and 'end', e.g. average_s_local_clustering_coefficient
        y = [
            func(**func_params, start=tid, end=tid)
            for tid in h.temporal_snapshots_ids()
        ]

    if rolling:
        y = __rolling_mean(y, window=rolling)

    data = pd.DataFrame({"Time": h.temporal_snapshots_ids(), "Value": y})
    chart = alt.Chart(data).mark_line().encode(
        x="Time:O",  # Ordinal encoding for time
        y="Value:Q"  # Quantitative encoding for values
    )
    return chart


def plot_attribute_dynamics(
    h: ASH,
    attr_name: str,
    func: Callable,
    func_params: dict = None,
    rolling: int = None,
    **kwargs
) -> alt.Chart:
    """
    :param h: ASH instance
    :param attr_name: attribute name
    :param func: function to be called at each timestamp
    :param func_params: parameters of the above function in key-value pairs
    :param rolling: size of the rolling window
    :param kwargs: Additional keyword arguments (not used in Altair)
    :return: Altair Chart object
    """
    if func_params is None:
        func_params = {}

    if "h" in func.__code__.co_varnames:  # e.g., inclusiveness
        func_params.update({"h": h})

    res = defaultdict(list)

    for tid in h.temporal_snapshots_ids():
        res_t = func(**func_params, tid=tid)[attr_name]
        if isinstance(res_t, dict):  # if result is by label
            for label in res_t:
                res[label].append(res_t[label])
        else:  # if result is aggregated
            res[attr_name].append(res_t)

    data = []
    for name, y in res.items():
        if rolling:
            y = __rolling_mean(y, window=rolling)
        data.extend(
            {"Time": tid, "Value": val, "Label": name}
            for tid, val in zip(h.temporal_snapshots_ids(), y)
        )

    data = pd.DataFrame(data)
    chart = alt.Chart(data).mark_line().encode(
        x="Time:O",
        y="Value:Q",
        color="Label:N"  # Different lines for each label
    )
    return chart


def plot_consistency(h, **kwargs) -> alt.Chart:
    """
    Plot the kde of the distribution of the consistency values for all nodes in the ASH.
    Given a node and an attribute, the node's consistency w.r.t. the attribute is the complementary of the entropy
    computed on the set of the attribute's values the node holds in time.

    :param h: ASH instance
    :param kwargs: Additional keyword arguments (not used in Altair)
    :return: Altair Chart object
    """
    cons = consistency(h)
    data = []
    for attr_name in list(cons.values())[0]:
        y = [v[attr_name] for v in cons.values()]
        data.extend({"Value": val, "Attribute": attr_name} for val in y)

    data = pd.DataFrame(data)
    chart = alt.Chart(data).transform_density(
        density="Value",
        groupby=["Attribute"],
        as_=["Value", "Density"]
    ).mark_line().encode(
        x="Value:Q",
        y="Density:Q",
        color="Attribute:N"
    ).properties(
        width=600,
        height=400
    )
    return chart
```

### Key Notes:
1. **Altair Charts**: Each function now returns an `alt.Chart` object instead of modifying a `matplotlib` axis.
2. **Data Preparation**: Altair requires data in a tidy format (long-form DataFrame). Data is reshaped accordingly.
3. **KDE Plot**: The `plot_consistency` function uses `transform_density` to approximate the KDE functionality.
4. **Heatmap**: The commented-out heatmap function (`plot_temporal_attribute_distribution`) can be implemented using `mark_rect` if needed. Let me know if you want that part migrated as well.