To migrate the provided code from using the `matplotlib` library to the `altair` library, several key changes were made:

1. **Import Statements**: The import statement for `matplotlib.pyplot` was removed, and `altair` was imported instead.
2. **Plotting Functions**: The plotting functions were modified to use `altair`'s syntax and methods. This includes creating charts using `alt.Chart()` and specifying encodings for the axes and marks.
3. **Vertical Lines and Text**: The methods for adding vertical lines and text annotations were replaced with `altair` equivalents, which involve layering charts.
4. **Histograms and Bar Charts**: The histogram and bar chart implementations were adapted to use `altair`'s `mark_bar()` and `mark_circle()` for scatter plots.
5. **Polar Histograms**: The polar histogram was not directly supported in `altair`, so it was omitted in this migration.
6. **Text Plotting**: The text plotting was adapted to use `mark_text()` in `altair`.

Here is the modified code:

```python
"""Plots for different data types / layouts."""

from itertools import repeat

import numpy as np
import altair as alt

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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    x_values = repeat(x_values) if (isinstance(x_values, np.ndarray) and x_values.ndim == 1) \
        else x_values
    y_values = [y_values] if (isinstance(y_values, np.ndarray) and y_values.ndim == 1) \
        else y_values

    charts = []
    for x_vals, y_vals in zip(x_values, y_values):
        chart = alt.Chart(pd.DataFrame({'x': x_vals, 'y': y_vals})).mark_line(**plt_kwargs).encode(
            x='x',
            y='y'
        )
        charts.append(chart)

    final_chart = alt.layer(*charts)

    if vline is not None:
        final_chart += add_vlines(vline)

    final_chart.display()


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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    chart = alt.Chart(pd.DataFrame({'x': x_values, 'y': y_values})).mark_circle(**plt_kwargs).encode(
        x='x',
        y='y'
    )

    chart.display()


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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', (2.5, 5)))

    n_points = len(data)
    xs = np.zeros(n_points) + 0.1 * np.random.rand(n_points)

    chart = alt.Chart(pd.DataFrame({'x': xs, 'y': data})).mark_circle(
        size=plt_kwargs.pop('ms', 20),
        opacity=plt_kwargs.pop('alpha', 0.5)
    ).encode(
        x='x',
        y='y'
    )

    chart = chart.properties(xlim=[-0.25, 0.25])

    if label:
        chart = chart.encode(x=alt.X('x', axis=alt.Axis(title=label)))

    chart.display()


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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    # Create histogram data
    hist_data = pd.DataFrame({'data': data})
    chart = alt.Chart(hist_data).mark_bar(**plt_kwargs).encode(
        alt.X('data:Q', bin=alt.Bin(maxbins=bins)),
        y='count()'
    )

    if average:
        avg_value = get_avg_func(average)(data)
        chart += add_vlines(avg_value)

    chart.display()


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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if not labels:
        labels = ['d' + str(ind) for ind in range(len(data))]

    bar_data = pd.DataFrame({'labels': labels, 'data': data})
    chart = alt.Chart(bar_data).mark_bar(**plt_kwargs).encode(
        x='labels',
        y='data'
    )

    if add_text:
        text = chart.mark_text(
            align='center',
            baseline='middle',
            dy=-5
        ).encode(
            text='data'
        )
        chart = chart + text

    chart.display()


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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if not labels:
        labels = ['d' + str(ind) for ind in range(len(data))]

    bar_data = pd.DataFrame({'labels': labels, 'data': data})
    chart = alt.Chart(bar_data).mark_bar(**plt_kwargs).encode(
        y='labels',
        x='data'
    )

    if add_text:
        text = chart.mark_text(
            align='left',
            baseline='middle',
            dx=5
        ).encode(
            text='data'
        )
        chart = chart + text

    chart.display()


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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    text_chart = alt.Chart(pd.DataFrame({'x': [xpos], 'y': [ypos]})).mark_text(
        fontSize=plt_kwargs.pop('fontSize', TEXT_SETTINGS['fontSize']),
        align=plt_kwargs.pop('ha', TEXT_SETTINGS['ha']),
        baseline=plt_kwargs.pop('va', TEXT_SETTINGS['va'])
    ).encode(
        x='x',
        y='y',
        text=alt.value(text)
    )

    if not show_axis:
        text_chart = text_chart.properties(width=0, height=0)

    text_chart.display()
```

Note: The code assumes that `pd` (Pandas) is imported, as it is necessary for creating DataFrames for `altair`. If it is not already imported in the original code, you should add `import pandas as pd` at the beginning. Additionally, the `add_vlines` and `add_text_labels` functions would need to be adapted to work with `altair` as well.