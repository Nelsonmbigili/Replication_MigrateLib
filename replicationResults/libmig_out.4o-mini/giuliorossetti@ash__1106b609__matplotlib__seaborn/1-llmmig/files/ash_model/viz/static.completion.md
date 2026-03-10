### Explanation of Changes
To migrate the provided code from using `matplotlib` to `seaborn`, the following changes were made:

1. **Import Statement**: The import statement for `matplotlib.pyplot` was replaced with `seaborn` since we will be using seaborn's plotting functions.
2. **Plotting Functions**: The `ax.plot()` and `ax.bar()` functions from `matplotlib` were replaced with `sns.scatterplot()` for scatter plots and `sns.barplot()` for bar plots, which are more suited for the types of plots being created.
3. **Legend Handling**: The legend handling was adjusted to fit with seaborn's style, which automatically handles legends in many cases.
4. **Logarithmic Scale**: The log-log scale handling was modified to use `ax.set_xscale('log')` and `ax.set_yscale('log')` instead of `ax.loglog()`, as seaborn does not have a direct equivalent for this.

### Modified Code
Here is the modified code after migrating to `seaborn`:

```python
import seaborn as sns

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
    :return: The axes object
    """

    if "ax" not in kwargs:
        ax = plt.gca()
    else:
        ax = kwargs["ax"]

    nodes = h.get_node_set()
    ss = np.arange(1, smax + 1, 1)
    degs = {s: {n: 0 for n in nodes} for s in ss}
    for n in nodes:
        for s in ss:
            degs[s][n] = h.get_s_degree(n, s)
    for s in ss:
        deg = dict(sorted(degs[s].items(), key=lambda item: item[1], reverse=True))

        y = np.bincount(list(deg.values()))

        sns.scatterplot(
            x=range(0, len(y)),
            y=y,
            label="s_" + str(s),
            alpha=0.8,
            ax=ax,
            **{k: v for k, v in kwargs.items() if k != "ax"}
        )
        if loglog:
            ax.set_xscale('log')
            ax.set_yscale('log')

        ax.legend()
    return ax


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
    :return: The axes object
    """

    if "ax" not in kwargs:
        ax = plt.gca()
    else:
        ax = kwargs["ax"]

    size_dist = dict(h.hyperedge_size_distribution())
    if max_size:
        size_dist = {k: v for k, v in size_dist.items() if k <= max_size}
    if min_size:
        size_dist = {k: v for k, v in size_dist.items() if k >= min_size}
    x, y = zip(*size_dist.items())

    sns.barplot(x=np.array(x), y=y, alpha=0.4, ax=ax, **{k: v for k, v in kwargs.items() if k != "ax"})
    return ax


def plot_degree_distribution(h: ASH, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_degree_distribution function plots the degree distribution of an ASH.
    The default is to draw a log-log plot.
    Matplotlib plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param loglog: Whether to plot the degree distribution in log-log scale
    :param kwargs: Pass matplotlib keyword arguments to the function
    :return: The axes object
    """

    if "ax" not in kwargs:
        ax = plt.gca()
    else:
        ax = kwargs["ax"]
    nodes = h.get_node_set()
    degs = {n: 0 for n in nodes}
    for n in nodes:
        degs[n] = h.get_degree(n)

    deg = dict(sorted(degs.items(), key=lambda item: item[1], reverse=True))
    y = list(deg.values())
    y = np.bincount(y)
    x = range(0, len(y))
    sns.scatterplot(x=x, y=y, alpha=0.4, ax=ax, **{k: v for k, v in kwargs.items() if k != "ax"})
    if loglog:
        ax.set_xscale('log')
        ax.set_yscale('log')
    return ax


def plot_s_ranks(h: ASH, smax: int, loglog: bool = True, **kwargs: object) -> object:
    """
    The plot_s_ranks function plots the s-degree distribution of a hypergraph.
    A line for each s will be plotted, from 1 to :smax: inclusive.
    Matplotlib plotting parameters (e.g., color) can be passed as **kwargs.

    :param h: ASH instance
    :param smax: Set the maximum value of s
    :param loglog: Specify whether the plot should be loglog or not
    :param kwargs: Pass matplotlib keyword arguments to the function
    :return: The axes object
    """
    if "ax" not in kwargs:
        ax = plt.gca()
    else:
        ax = kwargs["ax"]

    nodes = h.get_node_set()
    ss = np.arange(1, smax + 1, 1)
    degs = {s: {n: 0 for n in nodes} for s in ss}
    for n in nodes:
        for s in ss:
            degs[s][n] = h.get_s_degree(n, s)

    for s in ss:
        deg = dict(sorted(degs[s].items(), key=lambda item: item[1], reverse=True))

        y = list(deg.values())

        sns.scatterplot(
            x=range(len(y)),
            y=y,
            label="s_" + str(s),
            alpha=0.4,
            ax=ax,
            **{k: v for k, v in kwargs.items() if k != "ax"}
        )

        if loglog:
            ax.set_xscale('log')
            ax.set_yscale('log')
    return ax
```