### Explanation of Changes

To migrate the provided code from using `matplotlib` to `plotly`, the following changes were made:

1. **Importing Plotly**: The `matplotlib.pyplot` import was replaced with `plotly.graph_objects` for creating plots.
2. **Creating Figures**: Instead of using `plt.gca()` to get the current axes, a new figure and axes were created using `go.Figure()`.
3. **Plotting Data**: The plotting functions were modified to use `plotly`'s `add_trace()` method instead of `ax.plot()` and `ax.bar()`. The data was structured as `go.Scatter` for line plots and `go.Bar` for bar plots.
4. **Log-Log Scale**: The log-log scale was set using `update_yaxes(type="log")` and `update_xaxes(type="log")` instead of `ax.loglog()`.
5. **Returning the Figure**: Instead of returning the axes object, the modified functions now return the `plotly` figure object.

### Modified Code

```python
import plotly.graph_objects as go

from ash_model.measures import *


def plot_s_degrees(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_degrees function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Matplotlib plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass matplotlib keyword arguments to the function
    :return: The figure object
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
                x=range(0, len(y)),
                y=y,
                mode='markers',
                name="s_" + str(s),
                marker=dict(opacity=0.8),
                **{k: v for k, v in kwargs.items() if k != "ax"}
            )
        )
    if loglog:
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")

    fig.update_layout(legend=dict(x=0, y=1))
    return fig


def plot_hyperedge_size_distribution(
    h: ASH, max_size: int = None, min_size: int = None, **kwargs: object
) -> object:
    """
    The plot_hyperedge_size_distribution function plots the distribution of hyperedge sizes in a hypergraph.
    :min_size: and :max_size: can be used to filter out hyperedges.
    Matplotlib plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param max_size: Specify the maximum size of hyperedges to be plotted
    :param min_size: Specify the minimum size of hyperedges to be plotted
    :param kwargs: Pass matplotlib keyword arguments to the function
    :return: The figure object
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
            **{k: v for k, v in kwargs.items() if k != "ax"}
        )
    )
    return fig


def plot_degree_distribution(h: ASH, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_degree_distribution function plots the degree distribution of an ASH.
    The default is to draw a log-log plot.
    Matplotlib plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param loglog: Whether to plot the degree distribution in log-log scale
    :param kwargs: Pass matplotlib keyword arguments to the function
    :return: The figure object
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
            mode='markers',
            opacity=0.4,
            **{k: v for k, v in kwargs.items() if k != "ax"}
        )
    )
    if loglog:
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")
    return fig


def plot_s_ranks(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_ranks function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Matplotlib plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass matplotlib keyword arguments to the function
    :return: The figure object
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
                x=range(len(y)),
                y=y,
                mode='markers',
                name="s_" + str(s),
                opacity=0.4,
                **{k: v for k, v in kwargs.items() if k != "ax"}
            )
        )

        if loglog:
            fig.update_xaxes(type="log")
            fig.update_yaxes(type="log")
    return fig
```