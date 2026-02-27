### Explanation of Changes
The original code uses `matplotlib` for plotting, which is a procedural plotting library. To migrate to `altair`, which is a declarative statistical visualization library, the following changes were made:
1. **Import Changes**: Removed `matplotlib` imports and replaced them with `altair`.
2. **Plotting Logic**: Replaced `matplotlib` plotting functions (e.g., `ax.plot`, `ax.bar`, etc.) with equivalent `altair` chart definitions (e.g., `alt.Chart`, `alt.mark_line`, `alt.mark_bar`, etc.).
3. **Axis Handling**: Removed `ax` parameter and related logic since `altair` does not use explicit axis objects. Instead, axis properties are defined declaratively within the chart.
4. **Vertical Lines and Text Labels**: Replaced custom functions like `add_vlines` and `add_text_labels` with `altair` equivalents (e.g., `alt.rule` for vertical lines and `alt.text` for annotations).
5. **Figure Size**: Used `alt.Chart.properties` to set the figure size.
6. **Polar Plots**: `altair` does not natively support polar plots, so this functionality was omitted or would require a workaround (e.g., transforming data to polar coordinates manually).
7. **Text Plotting**: Used `alt.Chart.mark_text` for text rendering.

Below is the modified code using `altair`.

---

### Modified Code
```python
"""Plots for different data types / layouts."""

from itertools import repeat

import numpy as np
import altair as alt
import pandas as pd

from spiketools.measures.circular import bin_circular
from spiketools.utils.options import get_avg_func
from spiketools.plts.annotate import add_vlines, add_text_labels
from spiketools.plts.utils import savefig
from spiketools.plts.settings import TEXT_SETTINGS

###################################################################################################
###################################################################################################

@savefig
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

    x_values = repeat(x_values) if (isinstance(x_values, np.ndarray) and x_values.ndim == 1) \
        else x_values
    y_values = [y_values] if (isinstance(y_values, np.ndarray) and y_values.ndim == 1) \
        else y_values

    data = pd.DataFrame({'x': np.concatenate(x_values), 'y': np.concatenate(y_values)})
    chart = alt.Chart(data).mark_line().encode(
        x='x:Q',
        y='y:Q'
    )

    if vline:
        vline_data = pd.DataFrame({'x': vline})
        vline_chart = alt.Chart(vline_data).mark_rule(color='red').encode(x='x:Q')
        chart += vline_chart

    return chart.properties(**plt_kwargs)


@savefig
def plot_scatter(x_values, y_values, **plt_kwargs):
    """Plot 2d data as a scatter plot.

    Parameters
    ----------
    x_values, y_values : 1d or 2d array or list of 1d array
        Data to plot on the x and y axis.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    data = pd.DataFrame({'x': x_values, 'y': y_values})
    chart = alt.Chart(data).mark_point().encode(
        x='x:Q',
        y='y:Q'
    )

    return chart.properties(**plt_kwargs)


@savefig
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
    df = pd.DataFrame({'x': xs, 'y': data})

    chart = alt.Chart(df).mark_point(size=plt_kwargs.pop('ms', 20), opacity=plt_kwargs.pop('alpha', 0.5)).encode(
        x=alt.X('x:Q', axis=None),
        y='y:Q'
    )

    if label:
        chart = chart.properties(title=label)

    return chart.properties(**plt_kwargs)


@savefig
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

    df = pd.DataFrame({'data': data})
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('data:Q', bin=alt.Bin(maxbins=bins)),
        y='count()'
    )

    if average:
        avg_value = get_avg_func(average)(data)
        avg_line = alt.Chart(pd.DataFrame({'x': [avg_value]})).mark_rule(color='red').encode(x='x:Q')
        chart += avg_line

    return chart.properties(**plt_kwargs)


@savefig
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

    df = pd.DataFrame({'label': labels, 'value': data})
    chart = alt.Chart(df).mark_bar().encode(
        x='label:N',
        y='value:Q'
    )

    if add_text:
        text = chart.mark_text(dy=-10, color='white').encode(text='value:Q')
        chart += text

    return chart.properties(**plt_kwargs)


@savefig
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

    df = pd.DataFrame({'label': labels, 'value': data})
    chart = alt.Chart(df).mark_bar().encode(
        y='label:N',
        x='value:Q'
    )

    if add_text:
        text = chart.mark_text(dx=10, color='white').encode(text='value:Q')
        chart += text

    return chart.properties(**plt_kwargs)


@savefig
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

    df = pd.DataFrame({'x': [xpos], 'y': [ypos], 'text': [text]})
    chart = alt.Chart(df).mark_text(
        align='center',
        baseline='middle',
        fontSize=plt_kwargs.pop('fontsize', 12)
    ).encode(
        x='x:Q',
        y='y:Q',
        text='text:N'
    )

    if not show_axis:
        chart = chart.configure_axis(grid=False, domain=False, ticks=False, labels=False)

    return chart.properties(**plt_kwargs)
```

---

### Notes
- The `plot_polar_hist` function was omitted because `altair` does not natively support polar plots. A workaround would involve transforming the data into polar coordinates and using a custom visualization library.
- The `add_vlines` and `add_text_labels` functions were replaced with `altair` equivalents where applicable.
- The `plt_kwargs` are passed to `altair`'s `properties` method for setting chart properties like width and height.