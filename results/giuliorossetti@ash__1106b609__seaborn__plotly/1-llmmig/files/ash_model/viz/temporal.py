import pandas as pd
import plotly.graph_objects as go
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

    return fig


# def plot_temporal_attribute_distribution(h, attr_name, **kwargs):
#
#    tids = h.temporal_snapshots_ids()
#
#    labels = h.node_attributes_to_attribute_values()[attr_name]
#
#    distr = {label: {t: 0 for t in tids} for label in labels}
#
#    for t in tids:
#        nodes = h.get_node_set(tid=t)
#        node_count = 0
#        for node in nodes:
#            prof = h.get_node_profile(node, t)
#            attr = prof.get_attribute(attr_name)
#            distr[attr][t] += 1
#            node_count += 1
#
#        for label in labels:
#            distr[label][t] = distr[label][t] / node_count
#    data = pd.DataFrame(distr, columns=sorted(distr.keys())).transpose()
#    fig = go.Figure(data=go.Heatmap(z=data.values, x=data.columns, y=data.index, **kwargs))
#    return fig


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
        fig.add_trace(go.Histogram(x=y, name=attr_name, histnorm="probability", **kwargs))

    fig.update_layout(
        xaxis=dict(range=[-0.2, 1.2]),
        barmode="overlay",
        legend=dict(title="Attributes"),
    )
    return fig
