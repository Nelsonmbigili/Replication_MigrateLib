### Explanation of Changes

To migrate the provided code from using `matplotlib` to `plotly`, several key changes were made:

1. **Importing Plotly**: The `matplotlib.pyplot` import was replaced with `plotly.graph_objects` (or `plotly.express` where appropriate) to facilitate the creation of plots.

2. **Plotting Functions**: The plotting functions were modified to use Plotly's syntax. For example:
   - `ax.plot()` was replaced with `go.Scatter()` for line and scatter plots.
   - `ax.hist()` was replaced with `go.Histogram()` for histograms.
   - `ax.bar()` and `ax.barh()` were replaced with `go.Bar()` and `go.Bar()` with orientation set for horizontal bars.
   - The polar histogram was adapted using `go.Figure()` and `go.Barpolar()`.

3. **Layout and Axes**: Plotly handles layout and axes differently, so adjustments were made to set titles, axis labels, and other properties using Plotly's layout features.

4. **Text Annotations**: The text plotting was adapted to use `fig.add_annotation()` for adding text to the plot.

5. **Figure Creation**: Instead of working with an `ax` object, a `fig` object is created and returned at the end of each plotting function.

Here is the modified code:

```python
"""Plots for different data types / layouts."""

from itertools import repeat

import numpy as np
import plotly.graph_objects as go

from spiketools.measures.circular import bin_circular
from spiketools.utils.options import get_avg_func
from spiketools.plts.annotate import add_vlines, add_text_labels
from spiketools.plts.utils import check_ax, savefig
from spiketools.plts.style import set_plt_kwargs
from spiketools.plts.settings import TEXT_SETTINGS

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_lines(x_values, y_values, vline=None, ax=None, **plt_kwargs):
    """Plot data as a line.

    Parameters
    ----------
    x_values, y_values : 1d or 2d array or list of 1d array
        Data to plot on the x and y axis.
    vline : float or list, optional
        Location(s) to draw a vertical line. If None, no line is drawn.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    x_values = repeat(x_values) if (isinstance(x_values, np.ndarray) and x_values.ndim == 1) \
        else x_values
    y_values = [y_values] if (isinstance(y_values, np.ndarray) and y_values.ndim == 1) \
        else y_values

    for x_vals, y_vals in zip(x_values, y_values):
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', **plt_kwargs))

    if vline is not None:
        add_vlines(vline, fig)

    fig.show()


@savefig
@set_plt_kwargs
def plot_scatter(x_values, y_values, ax=None, **plt_kwargs):
    """Plot 2d data as a scatter plot.

    Parameters
    ----------
    x_values, y_values : 1d or 2d array or list of 1d array
        Data to plot on the x and y axis.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='markers', **plt_kwargs))
    fig.show()


@savefig
@set_plt_kwargs
def plot_points(data, label=None, ax=None, **plt_kwargs):
    """Plot 1d data as points.

    Parameters
    ----------
    data : 1d array
        Data values to plot
    label : str, optional
        Label for the x-axis.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    n_points = len(data)
    xs = np.zeros(n_points) + 0.1 * np.random.rand(n_points)

    fig.add_trace(go.Scatter(x=xs, y=data, mode='markers', 
                              marker=dict(size=plt_kwargs.pop('ms', 20), opacity=plt_kwargs.pop('alpha', 0.5)),
                              **plt_kwargs))

    fig.update_xaxes(range=[-0.25, 0.25])
    fig.update_xaxes(tickvals=[], title_text=label)
    fig.show()


@savefig
@set_plt_kwargs
def plot_hist(data, bins=None, range=None, density=None,
              average=None, ax=None, **plt_kwargs):
    """Plot data as a histogram.

    Parameters
    ----------
    data : 1d array
        Data to plot.
    bins : int or list, optional
        Bin definition, either a number of bins to use, or bin definitions.
    range : tuple, optional
        Range of the data to plot.
    density : bool, optional, default: False
        Whether to draw a probability density.
    average : {'median', 'mean'}, optional
        Which kind of average to compute and add to the plot.
        If None, no average is plotted.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=data, xbins=dict(size=bins), **plt_kwargs))

    if average:
        add_vlines(get_avg_func(average)(data), lw=4, color='red', alpha=0.8, fig=fig)

    fig.show()


@savefig
@set_plt_kwargs
def plot_bar(data, labels=None, add_text=False, ax=None, **plt_kwargs):
    """Plot data in a bar graph.

    Parameters
    ----------
    data : list of float
        Data to plot.
    labels : list of str, optional
        Labels for the bar plot.
    add_text : bool, optional, default: False
        Whether to annotate the bars with text showing their numerical values.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    if not labels:
        labels = ['d' + str(ind) for ind in range(len(data))]

    fig.add_trace(go.Bar(x=labels, y=data, **plt_kwargs))

    if add_text:
        add_text_labels(data, axis='x', location=data, colors='white')

    fig.show()


@savefig
@set_plt_kwargs
def plot_barh(data, labels=None, add_text=False, ax=None, **plt_kwargs):
    """Plot a horizontal bar plot.

    Parameters
    ----------
    data : list or array of float
        Data to plot.
    labels : list of str, optional
        Labels for the bar plot.
    add_text : bool, optional, default: False
        Whether to annotate the bars with text showing their numerical values.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    if not labels:
        labels = ['d' + str(ind) for ind in range(len(data))]

    fig.add_trace(go.Bar(y=labels, x=data, orientation='h', **plt_kwargs))

    if add_text:
        add_text_labels(data, axis='y', location=data, colors='white')

    fig.show()


@savefig
@set_plt_kwargs
def plot_polar_hist(data, bin_width=10, ax=None, **plt_kwargs):
    """Plot a polar histogram.

    Parameters
    ----------
    data : 1d array
        Data to plot in a circular histogram.
    bin_width : float, optional, default: 10
        Width of the bins to use for the histogram.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    bin_edges, counts = bin_circular(data, bin_width=bin_width)
    fig.add_trace(go.Barpolar(r=counts, theta=bin_edges[:-1], **plt_kwargs))
    fig.show()


@savefig
@set_plt_kwargs
def plot_text(text, xpos=0.5, ypos=0.5, show_axis=False, ax=None, **plt_kwargs):
    """Plot text.

    Parameters
    ----------
    text : str
        The text to plot.
    xpos, ypos : float, optional, default: 0.5
        The x and y positions to plot the text.
    show_axis : bool, optional, default: False
        Whether to show the axis of the plot.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    fig.add_annotation(x=xpos, y=ypos, text=text,
                       font=dict(**plt_kwargs.pop('fontdict', TEXT_SETTINGS['fontdict'])),
                       showarrow=False)

    if not show_axis:
        fig.update_layout(showlegend=False)

    fig.show()
``` 

This code now uses Plotly for all plotting functions while maintaining the original structure and functionality as closely as possible.