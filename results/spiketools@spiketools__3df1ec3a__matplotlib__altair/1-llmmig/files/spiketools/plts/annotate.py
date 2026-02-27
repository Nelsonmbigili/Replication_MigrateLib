"""Helper functions to annotate plots with extra elements / information."""

import pandas as pd
import altair as alt
from itertools import repeat
import numpy as np

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


def add_vlines(vline, **plt_kwargs):
    """Add vertical line(s) to a plot.

    Parameters
    ----------
    vline : float or list
        Location(s) of the vertical lines to add to the plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """
    vline = listify(vline)
    data = pd.DataFrame({'x': vline})
    return alt.Chart(data).mark_rule(**plt_kwargs).encode(x='x:Q')


def add_hlines(hline, **plt_kwargs):
    """Add horizontal line(s) to a plot.

    Parameters
    ----------
    hline : float or list
        Location(s) of the horizontal lines to add to the plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """
    hline = listify(hline)
    data = pd.DataFrame({'y': hline})
    return alt.Chart(data).mark_rule(**plt_kwargs).encode(y='y:Q')


def add_gridlines(x_bins, y_bins, **plt_kwargs):
    """Add gridlines to a plot.

    Parameters
    ----------
    x_bins, y_bins : list of float, optional
        Bin edges for each axis.
        If provided, these are used to draw grid lines on the plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """
    x_lines = add_vlines(x_bins, **plt_kwargs) if x_bins else None
    y_lines = add_hlines(y_bins, **plt_kwargs) if y_bins else None
    return (x_lines + y_lines) if x_lines and y_lines else (x_lines or y_lines)


def add_vshades(vshades, **plt_kwargs):
    """Add vertical shade region(s) to a plot.

    Parameters
    ----------
    vshade : list of float or list of list of float
        Region(s) of the plot to shade in.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """
    vshades = listify(vshades, index=True)
    data = pd.DataFrame(vshades, columns=['x1', 'x2'])
    return alt.Chart(data).mark_rect(**plt_kwargs).encode(
        x='x1:Q',
        x2='x2:Q'
    )


def add_hshades(hshades, **plt_kwargs):
    """Add horizontal shade region(s) to a plot.

    Parameters
    ----------
    hshade : list of float
        Region(s) of the plot to shade in.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """
    hshades = listify(hshades, index=True)
    data = pd.DataFrame(hshades, columns=['y1', 'y2'])
    return alt.Chart(data).mark_rect(**plt_kwargs).encode(
        y='y1:Q',
        y2='y2:Q'
    )


def add_box_shade(x1, x2, y_val, y_range=0.41, **plt_kwargs):
    """Add a shaded box to a plot.

    Parameters
    ----------
    x1, x2 : float
        The start and end positions for the shaded box on the x-axis.
    y_val : float
        The position of the shaded box on the y-axis.
    y_range : float
        The range, as +/-, around the y position to shade the box.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """
    data = pd.DataFrame({'x1': [x1], 'x2': [x2], 'y1': [y_val - y_range], 'y2': [y_val + y_range]})
    return alt.Chart(data).mark_rect(**plt_kwargs).encode(
        x='x1:Q',
        x2='x2:Q',
        y='y1:Q',
        y2='y2:Q'
    )


def add_dots(dots, **plt_kwargs):
    """Add dots to a plot.

    Parameters
    ----------
    dots : 1d or 2d array
        Definitions of the dots to add to the plot.
        If 1d array, defines a single dot as [x_pos, y_pos].
        If 2d array, 0th row is x-pos and 1th row is y-pos for multiple dot positions.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """
    dots = np.atleast_2d(dots).T if dots.ndim == 1 else dots
    data = pd.DataFrame({'x': dots[0, :], 'y': dots[1, :]})
    return alt.Chart(data).mark_point(**plt_kwargs).encode(
        x='x:Q',
        y='y:Q'
    )


def add_significance(stats, sig_level=0.05, x_vals=None):
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
    """
    if not isinstance(stats[0], (float)):
        stats = [stat.pvalue for stat in stats]

    data = pd.DataFrame({'x': x_vals, 'p_value': stats})
    data['significant'] = data['p_value'] < sig_level

    return alt.Chart(data).mark_point(shape='*', color='black').encode(
        x='x:Q',
        y=alt.value(0),
        opacity=alt.condition('datum.significant', alt.value(1), alt.value(0))
    )


def add_text_labels(texts, location='start', axis='x', offset=None,
                    values=None, colors='black', **plt_kwargs):
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
    """
    values = range(len(texts)) if values is None else values
    data = pd.DataFrame({'text': texts, 'value': values, 'color': listify(colors)})

    if axis == 'x':
        return alt.Chart(data).mark_text(dy=offset, **plt_kwargs).encode(
            x='value:Q',
            text='text:N',
            color='color:N'
        )
    elif axis == 'y':
        return alt.Chart(data).mark_text(dx=offset, **plt_kwargs).encode(
            y='value:Q',
            text='text:N',
            color='color:N'
        )
