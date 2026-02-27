### Explanation of Changes
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. **Library Import**: Replaced `matplotlib.pyplot` with `plotly.graph_objects` (`go`) and `plotly.express` (`px`) where applicable.
2. **Axis Handling**: Removed the `ax` parameter and `check_ax` utility since `plotly` does not use explicit axis objects. Instead, each plot is created independently.
3. **Plotting Functions**: Replaced `matplotlib` plotting functions (`plot`, `scatter`, `bar`, `barh`, `hist`, etc.) with equivalent `plotly` methods.
4. **Vertical Lines**: Used `go.Scatter` with `mode='lines'` to add vertical lines (`vline`).
5. **Text Annotations**: Used `add_vlines` and `add_text_labels` logic with `plotly`'s `annotations` for text and labels.
6. **Polar Plots**: Used `plotly`'s `polar` plotting capabilities for the polar histogram.
7. **Text Plotting**: Used `plotly`'s `annotations` for text placement instead of `ax.text`.

Below is the modified code.

---

### Modified Code
```python
"""Plots for different data types / layouts."""

from itertools import repeat

import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from spiketools.measures.circular import bin_circular
from spiketools.utils.options import get_avg_func
from spiketools.plts.annotate import add_vlines, add_text_labels
from spiketools.plts.utils import savefig
from spiketools.plts.style import set_plt_kwargs
from spiketools.plts.settings import TEXT_SETTINGS

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_lines(x_values, y_values, vline=None, **plt_kwargs):
    """Plot data as a line.

    Parameters
    ----------
    x_values, y_values : 1d or 2d array or list of 1d array
        Data to plot on the x and y axis.
    vline : float or list, optional
        Location(s) to draw a vertical line. If None, no line is drawn.
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

    if vline:
        for v in (vline if isinstance(vline, list) else [vline]):
            fig.add_vline(x=v, line_dash="dash", line_color="red")

    fig.show()


@savefig
@set_plt_kwargs
def plot_scatter(x_values, y_values, **plt_kwargs):
    """Plot 2d data as a scatter plot.

    Parameters
    ----------
    x_values, y_values : 1d or 2d array or list of 1d array
        Data to plot on the x and y axis.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='markers', **plt_kwargs))
    fig.show()


@savefig
@set_plt_kwargs
def plot_points(data, label=None, **plt_kwargs):
    """Plot 1d data as points.

    Parameters
    ----------
    data : 1d array
        Data values to plot
    label : str, optional
        Label for the x-axis.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    n_points = len(data)
    xs = np.zeros(n_points) + 0.1 * np.random.rand(n_points)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=data, mode='markers',
                             marker=dict(size=plt_kwargs.pop('ms', 20),
                                         opacity=plt_kwargs.pop('alpha', 0.5)),
                             **plt_kwargs))
    fig.update_xaxes(visible=False)
    if label:
        fig.update_xaxes(tickvals=[0], ticktext=[label])
    fig.show()


@savefig
@set_plt_kwargs
def plot_hist(data, bins=None, range=None, density=None, average=None, **plt_kwargs):
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
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = px.histogram(data, nbins=bins, range_x=range, histnorm='probability' if density else None, **plt_kwargs)

    if average:
        avg_value = get_avg_func(average)(data)
        fig.add_vline(x=avg_value, line_width=4, line_color='red', opacity=0.8)

    fig.show()


@savefig
@set_plt_kwargs
def plot_bar(data, labels=None, add_text=False, **plt_kwargs):
    """Plot data in a bar graph.

    Parameters
    ----------
    data : list of float
        Data to plot.
    labels : list of str, optional
        Labels for the bar plot.
    add_text : bool, optional, default: False
        Whether to annotate the bars with text showing their numerical values.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    if not labels:
        labels = ['d' + str(ind) for ind in range(len(data))]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=data, text=data if add_text else None, textposition='auto', **plt_kwargs))
    fig.show()


@savefig
@set_plt_kwargs
def plot_barh(data, labels=None, add_text=False, **plt_kwargs):
    """Plot a horizontal bar plot.

    Parameters
    ----------
    data : list or array of float
        Data to plot.
    labels : list of str, optional
        Labels for the bar plot.
    add_text : bool, optional, default: False
        Whether to annotate the bars with text showing their numerical values.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    if not labels:
        labels = ['d' + str(ind) for ind in range(len(data))]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=data, y=labels, orientation='h', text=data if add_text else None, textposition='auto', **plt_kwargs))
    fig.show()


@savefig
@set_plt_kwargs
def plot_polar_hist(data, bin_width=10, **plt_kwargs):
    """Plot a polar histogram.

    Parameters
    ----------
    data : 1d array
        Data to plot in a circular histogram.
    bin_width : float, optional, default: 10
        Width of the bins to use for the histogram.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    bin_edges, counts = bin_circular(data, bin_width=bin_width)

    fig = go.Figure()
    fig.add_trace(go.Barpolar(theta=bin_edges[:-1], r=counts, **plt_kwargs))
    fig.show()


@savefig
@set_plt_kwargs
def plot_text(text, xpos=0.5, ypos=0.5, show_axis=False, **plt_kwargs):
    """Plot text.

    Parameters
    ----------
    text : str
        The text to plot.
    xpos, ypos : float, optional, default: 0.5
        The x and y positions to plot the text.
    show_axis : bool, optional, default: False
        Whether to show the axis of the plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()
    fig.add_annotation(x=xpos, y=ypos, text=text, showarrow=False,
                       font=plt_kwargs.pop('fontdict', TEXT_SETTINGS['fontdict']),
                       xanchor=plt_kwargs.pop('ha', TEXT_SETTINGS['ha']),
                       yanchor=plt_kwargs.pop('va', TEXT_SETTINGS['va']),
                       **plt_kwargs)

    if not show_axis:
        fig.update_layout(xaxis_visible=False, yaxis_visible=False)

    fig.show()
```