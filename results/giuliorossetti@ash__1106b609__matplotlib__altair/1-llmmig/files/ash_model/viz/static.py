import altair as alt
import pandas as pd
import numpy as np
from ash_model.measures import *


def plot_s_degrees(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_degrees function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Altair plotting parameters can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass Altair keyword arguments to the function
    :return: The Altair chart object
    """
    nodes = h.get_node_set()
    ss = np.arange(1, smax + 1, 1)
    data = []

    for n in nodes:
        for s in ss:
            degree = h.get_s_degree(n, s)
            data.append({"node": n, "s": s, "degree": degree})

    df = pd.DataFrame(data)

    # Aggregate degree counts for each s
    df_counts = df.groupby(["s", "degree"]).size().reset_index(name="count")

    # Create the Altair chart
    chart = alt.Chart(df_counts).mark_line(point=True).encode(
        x=alt.X("degree:Q", scale=alt.Scale(type="log" if loglog else "linear")),
        y=alt.Y("count:Q", scale=alt.Scale(type="log" if loglog else "linear")),
        color="s:N",
        tooltip=["s:N", "degree:Q", "count:Q"]
    ).properties(**kwargs)

    return chart


def plot_hyperedge_size_distribution(
    h: ASH, max_size: int = None, min_size: int = None, **kwargs: object
) -> object:
    """
    The plot_hyperedge_size_distribution function plots the distribution of hyperedge sizes in a hypergraph.
    :min_size: and :max_size: can be used to filter out hyperedges.
    Altair plotting parameters can be passed as **kwargs.

    :param h: ASH instance
    :param max_size: Specify the maximum size of hyperedges to be plotted
    :param min_size: Specify the minimum size of hyperedges to be plotted
    :param kwargs: Pass Altair keyword arguments to the function
    :return: The Altair chart object
    """
    size_dist = dict(h.hyperedge_size_distribution())
    if max_size:
        size_dist = {k: v for k, v in size_dist.items() if k <= max_size}
    if min_size:
        size_dist = {k: v for k, v in size_dist.items() if k >= min_size}

    df = pd.DataFrame(list(size_dist.items()), columns=["size", "count"])

    # Create the Altair bar chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("size:Q", title="Hyperedge Size"),
        y=alt.Y("count:Q", title="Count"),
        tooltip=["size:Q", "count:Q"]
    ).properties(**kwargs)

    return chart


def plot_degree_distribution(h: ASH, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_degree_distribution function plots the degree distribution of an ASH.
    The default is to draw a log-log plot.
    Altair plotting parameters can be passed as **kwargs.

    :param h: ASH instance
    :param loglog: Whether to plot the degree distribution in log-log scale
    :param kwargs: Pass Altair keyword arguments to the function
    :return: The Altair chart object
    """
    nodes = h.get_node_set()
    degs = {n: h.get_degree(n) for n in nodes}

    y = np.bincount(list(degs.values()))
    df = pd.DataFrame({"degree": range(len(y)), "count": y})

    # Create the Altair chart
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("degree:Q", scale=alt.Scale(type="log" if loglog else "linear")),
        y=alt.Y("count:Q", scale=alt.Scale(type="log" if loglog else "linear")),
        tooltip=["degree:Q", "count:Q"]
    ).properties(**kwargs)

    return chart


def plot_s_ranks(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_ranks function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Altair plotting parameters can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass Altair keyword arguments to the function
    :return: The Altair chart object
    """
    nodes = h.get_node_set()
    ss = np.arange(1, smax + 1, 1)
    data = []

    for n in nodes:
        for s in ss:
            degree = h.get_s_degree(n, s)
            data.append({"node": n, "s": s, "rank": degree})

    df = pd.DataFrame(data)

    # Create the Altair chart
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("rank:Q", scale=alt.Scale(type="log" if loglog else "linear")),
        y=alt.Y("rank:Q", scale=alt.Scale(type="log" if loglog else "linear")),
        color="s:N",
        tooltip=["s:N", "rank:Q"]
    ).properties(**kwargs)

    return chart
