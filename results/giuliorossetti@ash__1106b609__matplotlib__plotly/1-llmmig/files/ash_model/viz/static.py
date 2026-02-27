import plotly.graph_objects as go
import numpy as np
from ash_model.measures import *


def plot_s_degrees(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_degrees function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Plotly plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass plotly keyword arguments to the function
    :return: The plotly Figure object
    """
    fig = go.Figure()

    nodes = h.get_node_set()
    ss = np.arange(1, smax + 1, 1)
    degs = {s: {n: 0 for n in nodes} for s in ss}
    for n in nodes:
        for s in ss:
            degs[s][n] = h.get_s_degree(n, s)
    for s in ss:
        deg = dict(sorted(degs[s].items(), key=lambda item: item[1], reverse=True))

        y = np.bincount(list(deg.values()))

        fig.add_trace(
            go.Scatter(
                x=list(range(0, len(y))),
                y=y,
                mode="markers",
                name="s_" + str(s),
                opacity=0.8,
                **kwargs
            )
        )

    if loglog:
        fig.update_layout(
            xaxis_type="log",
            yaxis_type="log",
        )

    fig.update_layout(title="S-Degree Distribution", legend_title="s")
    return fig


def plot_hyperedge_size_distribution(
    h: ASH, max_size: int = None, min_size: int = None, **kwargs: object
) -> object:
    """
    The plot_hyperedge_size_distribution function plots the distribution of hyperedge sizes in a hypergraph.
    :min_size: and :max_size: can be used to filter out hyperedges.
    Plotly plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param max_size: Specify the maximum size of hyperedges to be plotted
    :param min_size: Specify the minimum size of hyperedges to be plotted
    :param kwargs: Pass plotly keyword arguments to the function
    :return: The plotly Figure object
    """
    fig = go.Figure()

    size_dist = dict(h.hyperedge_size_distribution())
    if max_size:
        size_dist = {k: v for k, v in size_dist.items() if k <= max_size}
    if min_size:
        size_dist = {k: v for k, v in size_dist.items() if k >= min_size}
    x, y = zip(*size_dist.items())

    fig.add_trace(
        go.Bar(
            x=np.array(x),
            y=y,
            opacity=0.4,
            **kwargs
        )
    )

    fig.update_layout(title="Hyperedge Size Distribution")
    return fig


def plot_degree_distribution(h: ASH, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_degree_distribution function plots the degree distribution of an ASH.
    The default is to draw a log-log plot.
    Plotly plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param loglog: Whether to plot the degree distribution in log-log scale
    :param kwargs: Pass plotly keyword arguments to the function
    :return: The plotly Figure object
    """
    fig = go.Figure()

    nodes = h.get_node_set()
    degs = {n: 0 for n in nodes}
    for n in nodes:
        degs[n] = h.get_degree(n)

    deg = dict(sorted(degs.items(), key=lambda item: item[1], reverse=True))
    y = list(deg.values())
    y = np.bincount(y)
    x = range(0, len(y))

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            opacity=0.4,
            **kwargs
        )
    )

    if loglog:
        fig.update_layout(
            xaxis_type="log",
            yaxis_type="log",
        )

    fig.update_layout(title="Degree Distribution")
    return fig


def plot_s_ranks(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_ranks function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Plotly plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass plotly keyword arguments to the function
    :return: The plotly Figure object
    """
    fig = go.Figure()

    nodes = h.get_node_set()
    ss = np.arange(1, smax + 1, 1)
    degs = {s: {n: 0 for n in nodes} for s in ss}
    for n in nodes:
        for s in ss:
            degs[s][n] = h.get_s_degree(n, s)

    for s in ss:
        deg = dict(sorted(degs[s].items(), key=lambda item: item[1], reverse=True))

        y = list(deg.values())

        fig.add_trace(
            go.Scatter(
                x=list(range(len(y))),
                y=y,
                mode="markers",
                name="s_" + str(s),
                opacity=0.4,
                **kwargs
            )
        )

    if loglog:
        fig.update_layout(
            xaxis_type="log",
            yaxis_type="log",
        )

    fig.update_layout(title="S-Rank Distribution", legend_title="s")
    return fig
