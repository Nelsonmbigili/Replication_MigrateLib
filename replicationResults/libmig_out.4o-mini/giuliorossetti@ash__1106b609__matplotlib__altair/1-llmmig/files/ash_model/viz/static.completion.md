### Explanation of Changes

To migrate the provided code from using `matplotlib` to `altair`, several key changes were made:

1. **Importing Altair**: The `matplotlib.pyplot` import was replaced with `import altair as alt`.
2. **Data Preparation**: Instead of plotting directly on axes, we create a DataFrame using `pandas` to hold the data for plotting.
3. **Plotting**: The plotting functions were changed to use Altair's syntax, which involves creating charts using the `Chart` class and specifying the encoding for the x and y axes.
4. **Legend and Axis Scaling**: Altair handles legends and axis scaling differently, so these were adjusted accordingly.
5. **Return Value**: Instead of returning an axes object, the functions now return the Altair chart object.

### Modified Code

```python
import altair as alt
import pandas as pd
import numpy as np

from ash_model.measures import *


def plot_s_degrees(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_degrees function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Altair plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass altair keyword arguments to the function
    :return: The chart object
    """

    nodes = h.get_node_set()
    ss = np.arange(1, smax + 1, 1)
    degs = {s: {n: 0 for n in nodes} for s in ss}
    for n in nodes:
        for s in ss:
            degs[s][n] = h.get_s_degree(n, s)

    charts = []
    for s in ss:
        deg = dict(sorted(degs[s].items(), key=lambda item: item[1], reverse=True))
        y = np.bincount(list(deg.values()))
        data = pd.DataFrame({'x': range(0, len(y)), 'y': y})

        chart = alt.Chart(data).mark_point().encode(
            x='x:Q',
            y='y:Q',
            tooltip=['x', 'y']
        ).properties(
            title=f's_{s}',
            **{k: v for k, v in kwargs.items() if k != "ax"}
        )
        charts.append(chart)

    final_chart = alt.layer(*charts).resolve_scale(y='shared')
    if loglog:
        final_chart = final_chart.transform_calculate(
            'log_x', 'log(x)',
            'log_y', 'log(y)'
        ).encode(
            x=alt.X('log_x:Q', title='log(x)'),
            y=alt.Y('log_y:Q', title='log(y)')
        )

    return final_chart


def plot_hyperedge_size_distribution(
    h: ASH, max_size: int = None, min_size: int = None, **kwargs: object
) -> object:
    """
    The plot_hyperedge_size_distribution function plots the distribution of hyperedge sizes in a hypergraph.
    :min_size: and :max_size: can be used to filter out hyperedges.
    Altair plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param max_size: Specify the maximum size of hyperedges to be plotted
    :param min_size: Specify the minimum size of hyperedges to be plotted
    :param kwargs: Pass altair keyword arguments to the function
    :return: The chart object
    """

    size_dist = dict(h.hyperedge_size_distribution())
    if max_size:
        size_dist = {k: v for k, v in size_dist.items() if k <= max_size}
    if min_size:
        size_dist = {k: v for k, v in size_dist.items() if k >= min_size}
    x, y = zip(*size_dist.items())
    data = pd.DataFrame({'x': x, 'y': y})

    chart = alt.Chart(data).mark_bar(opacity=0.4).encode(
        x='x:Q',
        y='y:Q',
        **{k: v for k, v in kwargs.items() if k != "ax"}
    )
    return chart


def plot_degree_distribution(h: ASH, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_degree_distribution function plots the degree distribution of an ASH.
    The default is to draw a log-log plot.
    Altair plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param loglog: Whether to plot the degree distribution in log-log scale
    :param kwargs: Pass altair keyword arguments to the function
    :return: The chart object
    """

    nodes = h.get_node_set()
    degs = {n: 0 for n in nodes}
    for n in nodes:
        degs[n] = h.get_degree(n)

    deg = dict(sorted(degs.items(), key=lambda item: item[1], reverse=True))
    y = list(deg.values())
    y = np.bincount(y)
    x = range(0, len(y))
    data = pd.DataFrame({'x': x, 'y': y})

    chart = alt.Chart(data).mark_point(opacity=0.4).encode(
        x='x:Q',
        y='y:Q',
        **{k: v for k, v in kwargs.items() if k != "ax"}
    )
    if loglog:
        chart = chart.transform_calculate(
            'log_x', 'log(x)',
            'log_y', 'log(y)'
        ).encode(
            x=alt.X('log_x:Q', title='log(x)'),
            y=alt.Y('log_y:Q', title='log(y)')
        )
    return chart


def plot_s_ranks(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_ranks function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Altair plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass altair keyword arguments to the function
    :return: The chart object
    """
    nodes = h.get_node_set()
    ss = np.arange(1, smax + 1, 1)
    degs = {s: {n: 0 for n in nodes} for s in ss}
    for n in nodes:
        for s in ss:
            degs[s][n] = h.get_s_degree(n, s)

    charts = []
    for s in ss:
        deg = dict(sorted(degs[s].items(), key=lambda item: item[1], reverse=True))
        y = list(deg.values())
        data = pd.DataFrame({'x': range(len(y)), 'y': y})

        chart = alt.Chart(data).mark_point(opacity=0.4).encode(
            x='x:Q',
            y='y:Q',
            tooltip=['x', 'y'],
            **{k: v for k, v in kwargs.items() if k != "ax"}
        ).properties(title=f's_{s}')
        charts.append(chart)

    final_chart = alt.layer(*charts).resolve_scale(y='shared')
    if loglog:
        final_chart = final_chart.transform_calculate(
            'log_x', 'log(x)',
            'log_y', 'log(y)'
        ).encode(
            x=alt.X('log_x:Q', title='log(x)'),
            y=alt.Y('log_y:Q', title='log(y)')
        )

    return final_chart
```