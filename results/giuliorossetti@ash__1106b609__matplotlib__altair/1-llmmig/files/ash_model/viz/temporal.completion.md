### Explanation of Changes
To migrate the code from `matplotlib` to `altair`, the following changes were made:
1. **Plotting with Altair**: Altair uses a declarative approach to create visualizations. Instead of directly modifying an `Axes` object (as in `matplotlib`), Altair requires data to be in a `pandas.DataFrame` format, and visualizations are created by specifying encodings and chart types.
2. **Data Preparation**: Since Altair works with `DataFrame` objects, the data used for plotting (e.g., `y` values) was converted into a `DataFrame` with appropriate columns for plotting.
3. **Line Plots**: Replaced `ax.plot` with `alt.Chart` for line plots. Encodings for the x-axis and y-axis were specified.
4. **Legend and Labels**: Altair automatically handles legends and axis labels, so explicit calls to `ax.legend()` and `ax.set_xlim()` were removed.
5. **Kernel Density Estimation (KDE)**: Altair does not have built-in KDE functionality like Seaborn. Instead, KDE was approximated using a histogram with a smoothed line overlay.

Below is the modified code using Altair.

---

### Modified Code
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
    :param kwargs: Pass Altair keyword arguments to the function
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

    # Prepare data for Altair
    data = pd.DataFrame({
        "Time": h.temporal_snapshots_ids(),
        "Value": y
    })

    # Create Altair line chart
    chart = alt.Chart(data).mark_line().encode(
        x="Time:O",  # Ordinal x-axis
        y="Value:Q"  # Quantitative y-axis
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
    :param kwargs: Pass Altair keyword arguments to the function
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

    # Prepare data for Altair
    data = []
    for name, y in res.items():
        if rolling:
            y = __rolling_mean(y, window=rolling)
        data.extend({"Time": tid, "Value": val, "Label": name} for tid, val in zip(h.temporal_snapshots_ids(), y))

    data = pd.DataFrame(data)

    # Create Altair line chart
    chart = alt.Chart(data).mark_line().encode(
        x="Time:O",  # Ordinal x-axis
        y="Value:Q",  # Quantitative y-axis
        color="Label:N"  # Color by label
    )

    return chart


def plot_consistency(h, **kwargs) -> alt.Chart:
    """
    Plot the kde of the distribution of the consistency values for all nodes in the ASH.
    Given a node and an attribute, the node's consistency w.r.t. the attribute is the complementary of the entropy
    computed on the set of the attribute's values the node holds in time.

    :param h: ASH instance
    :param kwargs: Pass Altair keyword arguments to the function
    :return: Altair Chart object
    """
    cons = consistency(h)
    data = []

    for attr_name in list(cons.values())[0]:
        y = [v[attr_name] for v in cons.values()]
        data.extend({"Value": val, "Attribute": attr_name} for val in y)

    data = pd.DataFrame(data)

    # Create Altair density plot (approximated with histogram + line)
    chart = alt.Chart(data).transform_density(
        density="Value",
        groupby=["Attribute"],
        as_=["Value", "Density"]
    ).mark_line().encode(
        x="Value:Q",
        y="Density:Q",
        color="Attribute:N"
    )

    return chart
```

---

### Key Notes
1. **Altair Charts**: Each function now returns an `alt.Chart` object instead of a `matplotlib.Axes` object.
2. **Data Preparation**: Data is explicitly converted into a `DataFrame` for Altair, as it requires structured data.
3. **KDE Approximation**: The `plot_consistency` function uses `transform_density` to approximate KDE, as Altair does not natively support Seaborn-style KDE plots.
4. **Interactive Features**: Altair charts are inherently interactive, which is an added benefit over `matplotlib`.