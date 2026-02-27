### Explanation of Changes
To migrate the code from `matplotlib` (version 3.10.1) to `plotly` (version 6.0.1), the following changes were made:
1. **Plotting Functions**:
   - Replaced `matplotlib`'s `ax.plot` with `plotly.graph_objects.Figure` and its `add_trace` method for line plots.
   - Replaced `seaborn.kdeplot` with `plotly`'s `Figure` and `add_trace` for kernel density estimation (KDE) plots.
   - Replaced `matplotlib`'s `ax.legend` with `plotly`'s `update_layout` to handle legends.
   - Replaced `matplotlib`'s `ax.set_xlim` with `plotly`'s `update_xaxes` for setting x-axis limits.
2. **Heatmap**:
   - The commented-out heatmap function was not migrated since it was not active in the original code.
3. **General Adjustments**:
   - Removed references to `ax` since `plotly` does not use axes objects in the same way as `matplotlib`.
   - Added `plotly.graph_objects` (`go`) for creating figures and traces.
   - Updated the return type of the plotting functions to return `plotly.graph_objects.Figure` instead of `matplotlib`'s `Axes`.

Below is the modified code.

---

### Modified Code
```python
import plotly.graph_objects as go
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
) -> object:
    """

    :param h: ASH instance
    :param func: function to be called at each timestamp
    :param func_params: parameters of the above function in key-value pairs
    :param rolling: size of the rolling window
    :param kwargs: Pass plotly keyword arguments to the function
    :return: The plotly Figure object
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

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=y, mode="lines", **kwargs))

    return fig


def plot_attribute_dynamics(
    h: ASH,
    attr_name: str,
    func: Callable,
    func_params: dict = None,
    rolling: int = None,
    **kwargs
) -> object:
    """

    :param h: ASH instance
    :param attr_name: attribute name
    :param func: function to be called at each timestamp
    :param func_params: parameters of the above function in key-value pairs
    :param rolling: size of the rolling window
    :param kwargs: Pass plotly keyword arguments to the function
    :return: The plotly Figure object
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

    fig = go.Figure()

    for name, y in res.items():
        if rolling:
            y = __rolling_mean(y, window=rolling)
        fig.add_trace(go.Scatter(y=y, mode="lines", name=name, **kwargs))

    fig.update_layout(legend_title="Attributes")
    return fig


def plot_consistency(h, **kwargs):
    """
    Plot the kde of the distribution of the consistency values for all nodes in the ASH.
    Given a node and an attribute, the node's consistency w.r.t. the attribute is the complementary of the entropy
    computed on the set of the attribute's values the node holds in time.

    :param h: ASH instance
    :param kwargs: Pass plotly keyword arguments to the function
    :return: The plotly Figure object
    """

    cons = consistency(h)
    fig = go.Figure()

    for attr_name in list(cons.values())[0]:
        y = [v[attr_name] for v in cons.values()]

        # Kernel density estimation is not directly supported in plotly, so we approximate it using histogram
        fig.add_trace(go.Histogram(x=y, name=attr_name, histnorm="probability", **kwargs))

    fig.update_layout(
        legend_title="Attributes",
        xaxis=dict(range=[-0.2, 1.2]),
        barmode="overlay",
    )
    return fig
```

---

### Key Notes
1. The `plotly` library uses `Figure` objects to manage plots, so the return type of the functions is now `plotly.graph_objects.Figure`.
2. KDE plots were approximated using `plotly`'s `Histogram` with `histnorm="probability"`, as `plotly` does not have a direct KDE function.
3. The heatmap function was not migrated since it was commented out in the original code. If needed, it can be implemented using `plotly`'s `imshow` or `heatmap` functionality.