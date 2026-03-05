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
) -> object:
    """
    :param h: ASH instance
    :param func: function to be called at each timestamp
    :param func_params: parameters of the above function in key-value pairs
    :param rolling: size of the rolling window
    :param kwargs: Pass altair keyword arguments to the function
    :return: The altair Chart object
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

    data = pd.DataFrame({'timestamp': h.temporal_snapshots_ids(), 'value': y})

    chart = alt.Chart(data).mark_line(**{k: v for k, v in kwargs.items() if k != "ax"}).encode(
        x='timestamp',
        y='value'
    )

    return chart

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
    :param kwargs: Pass altair keyword arguments to the function
    :return: The altair Chart object
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

    data = pd.DataFrame(res)

    if rolling:
        data = data.rolling(window=rolling).mean()

    chart = alt.Chart(data).mark_line(**{k: v for k, v in kwargs.items() if k != "ax"}).encode(
        x='index:O',
        y=alt.Y(attr_name, title=attr_name),
        color=alt.Color('key:N', legend=alt.Legend(title="Attributes"))
    )

    return chart

def plot_consistency(h, **kwargs):
    """
    Plot the kde of the distribution of the consistency values for all nodes in the ASH.
    Given a node and an attribute, the node's consistency w.r.t. the attribute is the complementary of the entropy
    computed on the set of the attribute's values the node holds in time.

    :param h: ASH instance
    :param kwargs: Pass altair keyword arguments to the function
    :return: The altair Chart object
    """
    cons = consistency(h)
    data = pd.DataFrame()

    for attr_name in list(cons.values())[0]:
        y = [v[attr_name] for v in cons.values()]
        temp_data = pd.DataFrame({'value': y, 'attribute': attr_name})
        data = pd.concat([data, temp_data], ignore_index=True)

    chart = alt.Chart(data).mark_area(opacity=0.5).encode(
        x='value:Q',
        y='count():Q',
        color='attribute:N'
    ).properties(
        width=400,
        height=300
    ).configure_range(
        category=alt.RangeScheme('category10')
    )

    return chart
