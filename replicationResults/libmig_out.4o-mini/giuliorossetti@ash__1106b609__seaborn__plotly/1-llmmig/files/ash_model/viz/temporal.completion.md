### Explanation of Changes

To migrate the provided code from using the `seaborn` library to the `plotly` library, the following changes were made:

1. **Import Statement**: The import for `seaborn` was removed, and `plotly.graph_objects` was imported to facilitate the creation of plots.
2. **Plotting Functions**: The `sns.kdeplot` function was replaced with `plotly.graph_objects.Scatter` to create line plots. The `plotly` library requires a different approach to create figures and add traces.
3. **Figure Creation**: Instead of using axes objects from `matplotlib`, a `plotly` figure object was created, and traces were added to this figure.
4. **Legend and Layout**: The legend and layout settings were adjusted to fit the `plotly` style.

The overall structure of the functions remains the same, but the plotting mechanism has been adapted to fit the `plotly` framework.

### Modified Code

```python
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

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
    :return: The figure object
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
    fig.add_trace(go.Scatter(y=y, **{k: v for k, v in kwargs.items()}))

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
    :return: The figure object
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
        fig.add_trace(go.Scatter(y=y, name=name, **{k: v for k, v in kwargs.items()}))

    fig.update_layout(legend=dict(title="Attributes"))

    return fig


def plot_consistency(h, **kwargs):
    """
    Plot the kde of the distribution of the consistency values for all nodes in the ASH.
    Given a node and an attribute, the node's consistency w.r.t. the attribute is the complementary of the entropy
    computed on the set of the attribute's values the node holds in time.

    :param h: ASH instance
    :param kwargs: Pass plotly keyword arguments to the function
    :return: The figure object
    """

    fig = go.Figure()

    cons = consistency(h)
    for attr_name in list(cons.values())[0]:
        y = [v[attr_name] for v in cons.values()]

        fig.add_trace(go.Scatter(y=y, mode='lines', name=attr_name, **{k: v for k, v in kwargs.items()}))

    fig.update_layout(xaxis=dict(range=(-0.2, 1.2), title='Consistency Values'),
                      yaxis_title='Density',
                      legend_title='Attributes')

    return fig
```