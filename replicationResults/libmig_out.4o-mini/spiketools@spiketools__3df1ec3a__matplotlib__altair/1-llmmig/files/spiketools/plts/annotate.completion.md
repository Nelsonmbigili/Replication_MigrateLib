To migrate the provided code from using the `matplotlib` library to the `altair` library, several key changes were made:

1. **Plotting Functions**: The `matplotlib` functions for adding lines, gridlines, and other elements to the plot (like `ax.axvline`, `ax.axhline`, `ax.fill_between`, etc.) were replaced with `altair` equivalents. In `altair`, we create visualizations using a declarative syntax, which means we define the data and the type of visualization rather than modifying an existing plot object.

2. **Data Handling**: `altair` works with data in a more structured way, typically using a `DataFrame` format. Therefore, the code was adjusted to prepare data accordingly.

3. **Color and Style**: The way colors and styles are applied in `altair` is different from `matplotlib`. Instead of passing parameters directly to plotting functions, we define them in the chart specifications.

4. **Gridlines and Shading**: The concept of gridlines and shading regions is handled differently in `altair`. Instead of setting ticks and gridlines on an axis, we define them as part of the chart's properties.

5. **Text Annotations**: Adding text labels in `altair` is done through the `mark_text` method, which is different from the `ax.text` method in `matplotlib`.

Here is the modified code using `altair`:

```python
"""Helper functions to annotate plots with extra elements / information."""

from itertools import repeat
import pandas as pd
import altair as alt

from spiketools.utils.base import listify
from spiketools.utils.checks import check_param_options

###################################################################################################
###################################################################################################

def color_pvalue(p_value, alpha=0.05, significant_color='red', null_color='black'):
    """Select a color based on the significance of a p-value.

    Parameters
    ----------
    p_value : float
        The p-value to check.
    alpha : float, optional, default: 0.05
        The significance level to check against.
    signicant_color : str, optional, default: 'red'
        The color for if the p-value is significant.
    null_color : str, optional, default: 'black'
        The color for if the p-value is not significant.

    Returns
    -------
    color : str
        Color value, reflecting the significance of the given p-value.
    """

    return significant_color if p_value < alpha else null_color


def add_vlines(vline, chart, **alt_kwargs):
    """Add vertical line(s) to a plot.

    Parameters
    ----------
    vline : float or list
        Location(s) of the vertical lines to add to the plot.
    chart : Chart
        Altair chart object to which to add the lines.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    if vline is not None:
        lines = pd.DataFrame({'vline': listify(vline)})
        line_chart = alt.Chart(lines).mark_rule(**alt_kwargs).encode(x='vline:Q')
        return chart + line_chart
    return chart


def add_hlines(hline, chart, **alt_kwargs):
    """Add horizontal line(s) to a plot.

    Parameters
    ----------
    hline : float or list
        Location(s) of the horizontal lines to add to the plot.
    chart : Chart
        Altair chart object to which to add the lines.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    if hline is not None:
        lines = pd.DataFrame({'hline': listify(hline)})
        line_chart = alt.Chart(lines).mark_rule(**alt_kwargs).encode(y='hline:Q')
        return chart + line_chart
    return chart


def add_gridlines(x_bins, y_bins, chart, **alt_kwargs):
    """Add gridlines to a plot.

    Parameters
    ----------
    x_bins, y_bins : list of float, optional
        Bin edges for each axis.
        If provided, these are used to draw grid lines on the plot.
    chart : Chart
        Altair chart object to update.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    if x_bins is not None:
        chart = chart.encode(x=alt.X('x:Q', scale=alt.Scale(domain=x_bins)))
    if y_bins is not None:
        chart = chart.encode(y=alt.Y('y:Q', scale=alt.Scale(domain=y_bins)))
    
    return chart


def add_vshades(vshades, chart, **alt_kwargs):
    """Add vertical shade region(s) to a plot.

    Parameters
    ----------
    vshade : list of float or list of list of float
        Region(s) of the plot to shade in.
    chart : Chart
        Altair chart object to which to add the shades.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    if vshades is not None:
        for vshade in listify(vshades, index=True):
            shade = pd.DataFrame({'start': [vshade[0]], 'end': [vshade[1]]})
            shade_chart = alt.Chart(shade).mark_area(opacity=0.2, **alt_kwargs).encode(x='start:Q', x2='end:Q')
            chart = chart + shade_chart
    return chart


def add_hshades(hshades, chart, **alt_kwargs):
    """Add horizontal shade region(s) to a plot.

    Parameters
    ----------
    hshade : list of float
        Region(s) of the plot to shade in.
    chart : Chart
        Altair chart object to which to add the shades.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    if hshades is not None:
        for hshade in listify(hshades, index=True):
            shade = pd.DataFrame({'start': [hshade[0]], 'end': [hshade[1]]})
            shade_chart = alt.Chart(shade).mark_area(opacity=0.2, **alt_kwargs).encode(y='start:Q', y2='end:Q')
            chart = chart + shade_chart
    return chart


def add_box_shade(x1, x2, y_val, y_range=0.41, chart, **alt_kwargs):
    """Add a shaded box to a plot.

    Parameters
    ----------
    x1, x2 : float
        The start and end positions for the shaded box on the x-axis.
    y_val : float
        The position of the shaded box on the y-axis.
    y_range : float
        The range, as +/-, around the y position to shade the box.
    chart : Chart
        Altair chart object to which to add the box.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    box = pd.DataFrame({'x1': [x1], 'x2': [x2], 'y1': [y_val - y_range], 'y2': [y_val + y_range]})
    box_chart = alt.Chart(box).mark_area(opacity=0.2, **alt_kwargs).encode(x='x1:Q', x2='x2:Q', y='y1:Q', y2='y2:Q')
    return chart + box_chart


def add_box_shades(x_values, y_values=None, x_range=1, y_range=0.41, chart, **alt_kwargs):
    """Add multiple shaded boxes to a plot.

    Parameters
    ----------
    x_values, y_values : 1d array
        Center position values for the x- and y-axes for each shaded box.
    x_range, y_range : float
        The range, as +/-, around the x and y positions to shade the box.
    chart : Chart
        Altair chart object to which to add the boxes.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    if y_values is None:
        y_values = range(0, len(x_values))

    for xval, yval in zip(x_values, y_values):
        chart = add_box_shade(xval - x_range, xval + x_range, yval, y_range, chart, **alt_kwargs)
    
    return chart


def add_dots(dots, chart, **alt_kwargs):
    """Add dots to a plot.

    Parameters
    ----------
    dots : 1d or 2d array
        Definitions of the dots to add to the plot.
        If 1d array, defines a single dot as [x_pos, y_pos].
        If 2d array, 0th row is x-pos and 1th row is y-pos for multiple dot positions.
    chart : Chart
        Altair chart object to which to add the dots.
    alt_kwargs
        Additional arguments to pass into the plot function.
    """

    if dots is not None:
        dots = pd.DataFrame(dots.T, columns=['x', 'y'])
        dot_chart = alt.Chart(dots).mark_point(**alt_kwargs).encode(x='x:Q', y='y:Q')
        return chart + dot_chart
    return chart


def add_significance(stats, sig_level=0.05, x_vals=None, chart=None):
    """Add markers to a plot to indicate statistical significance.

    Parameters
    ----------
    stats : list
        Statistical results, including p-values, to use to annotate the plot.
        List can contain floats, or statistical results if it has a `pvalue` field.
    sig_level : float, optional, default: 0.05
        Threshold level to consider a result significant.
    x_vals : 1d array, optional
        Values for the x-axis, for example time values or bin numbers.
        If not provided, x-values are accessed from the plot.
    chart : Chart
        Altair chart object to which to add significance markers.
    """

    if not x_vals:
        x_vals = range(len(stats))

    if not isinstance(stats[0], (float)):
        stats = [stat.pvalue for stat in stats]

    significance = pd.DataFrame({'x': x_vals, 'significant': [stat < sig_level for stat in stats]})
    sig_chart = alt.Chart(significance[significance['significant']]).mark_point(shape='star', color='black').encode(x='x:Q', y=alt.value(0))
    
    return chart + sig_chart


def add_text_labels(texts, location='start', axis='x', offset=None,
                    values=None, colors='black', chart=None, **alt_kwargs):
    """Add text to the side of a plot.

    Parameters
    ----------
    texts : list of str
        Text(s) to add to the plot.
    location : {'start', 'end'} or iterable
        Location to plot the text labels across the axis.
    axis : {'x', 'y'}
        Which axis to add text labels across.
    offset : float, optional
        An offset value to move the text.
        If not provided, default to 10% of the plot range.
    values : list of float, optional
        Position values to plot the text on the axis defined in `axis`.
        If not provided, defaults to the indices of the text labels.
    colors : str or list of str, optional
        Color(s) for each entry. Defaults to 'black'.
    chart : Chart
        Altair chart object to which to add the text labels.
    alt_kwargs
        Additional keyword arguments to pass to the `mark_text` call.
    """

    check_param_options(axis, 'axis', ['x', 'y'])

    plot_range = chart.encode().get('x', {}).get('scale', {}).get('domain', None) if axis == 'x' else chart.encode().get('y', {}).get('scale', {}).get('domain', None)

    if not offset:
        offset = 0.15 * (plot_range[1] - plot_range[0]) if plot_range else 0

    if not values:
        values = range(len(texts))

    colors = repeat(colors) if isinstance(colors, str) else colors

    if isinstance(location, str):
        check_param_options(location, 'location', ['start', 'end'])
        ind = {'start': 0, 'end': 1}[location]
        location = repeat(plot_range[ind])
    else:
        location = iter(location)
        offset = -offset

    text_data = pd.DataFrame({'text': texts, 'value': values, 'color': list(colors)})
    text_chart = alt.Chart(text_data).mark_text(**alt_kwargs).encode(
        x=alt.X('value:Q', title=None),
        y=alt.Y('value:Q', title=None),
        text='text:N',
        color='color:N'
    )
    
    return chart + text_chart
```

This modified code now uses `altair` for plotting, maintaining the original function signatures and logic while adapting to the new library's requirements.