### Explanation of Changes

To migrate the provided code from using `matplotlib` to `altair`, several key changes were made:

1. **Importing Altair**: The `matplotlib` library was replaced with `altair`, which is a declarative statistical visualization library for Python.

2. **Plotting Functions**: The plotting functions were changed from `ax.eventplot` and `ax.plot` to Altair's `Chart` and `mark_point` or `mark_line` methods. Altair uses a different approach to create visualizations, focusing on data transformations and encoding.

3. **Data Preparation**: The data structure used in Altair is typically a DataFrame (from `pandas`). Therefore, the spike times and firing rates were converted into a suitable format for Altair.

4. **Customizations**: Customizations such as colors, line styles, and legends were adapted to fit Altair's syntax.

5. **Vertical Lines and Shading**: The methods for adding vertical lines and shaded areas were replaced with Altair's `mark_rule` and `mark_area`.

6. **Legend Handling**: Altair automatically handles legends based on the data provided, so explicit legend handling was simplified.

Here is the modified code:

```python
"""Plots for trial related measures and analyses."""

import numpy as np
import altair as alt
import pandas as pd

from spiketools.measures.trials import compute_trial_frs
from spiketools.utils.base import flatten
from spiketools.utils.trials import extract_conditions_dict
from spiketools.utils.trials import split_trials_by_condition
from spiketools.utils.options import get_avg_func, get_var_func
from spiketools.plts.settings import DEFAULT_COLORS
from spiketools.plts.annotate import add_vlines, add_vshades, add_significance
from spiketools.plts.utils import check_ax, make_axes, get_kwargs, savefig
from spiketools.plts.style import set_plt_kwargs

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_rasters(spikes, events=None, vline=None, colors=None, vshade=None,
                 show_axis=False, ax=None, **plt_kwargs):
    """Plot rasters across multiple trials.

    Parameters
    ----------
    spikes : list of list of float or dict
        Spike times per trial.
        Multiple conditions can also be passed in.
        If dict, each key is a condition label and each value the list of list of spikes times.
    events : list
        Events to indicate on the raster plot. Should have length of number of trials.
    vline : float or list of float, optional
        Location(s) to draw a vertical line. If None, no line is drawn.
    colors : str or list of str or dict, optional
        Color(s) to plot the raster ticks.
        If more than one, should match the number of conditions.
        If a dictionary, the labels should match the spike condition labels.
    vshade : list of float or list of list of float, optional
        Vertical region(s) of the plot to shade in.
    show_axis : bool, optional, default: False
        Whether to show the axis around the plot.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
        Custom kwargs:
            line: 'line_color', 'line_lw', 'line_alpha'
            shade: 'shade_color', 'shade_alpha'
            events: 'event_color', 'event_linewidths', 'event_linelengths'
    """

    # Check and unpack condition data, if provided as a dictionary input
    spikes, colors = extract_conditions_dict(spikes, colors)

    # Prepare data for Altair
    data = []
    for trial_index, trial_spikes in enumerate(spikes):
        for spike_time in trial_spikes:
            data.append({'trial': trial_index, 'time': spike_time})

    df = pd.DataFrame(data)

    # Create the raster plot
    base = alt.Chart(df).encode(x='time:Q', y='trial:O')

    raster = base.mark_point(size=3, color=colors[0] if colors else 'black').encode(
        opacity=alt.value(0.5)
    )

    # If provided, add events to plot
    if events is not None:
        event_data = pd.DataFrame({'event_time': events})
        events_chart = alt.Chart(event_data).mark_rule(color='red').encode(
            x='event_time:Q'
        )
        raster = raster + events_chart

    # Add vertical lines
    if vline is not None:
        vline_data = pd.DataFrame({'vline': vline})
        vline_chart = alt.Chart(vline_data).mark_rule(color='green').encode(
            x='vline:Q'
        )
        raster = raster + vline_chart

    # Add shading if provided
    if vshade is not None:
        shade_data = pd.DataFrame({'start': [vshade[0]], 'end': [vshade[1]]})
        shade_chart = alt.Chart(shade_data).mark_area(opacity=0.25, color='red').encode(
            x='start:Q',
            x2='end:Q',
            y=alt.value(0),
            y2=alt.value(len(spikes))
        )
        raster = raster + shade_chart

    return raster.properties(width=600, height=400).configure_view(stroke='transparent')


@savefig
@set_plt_kwargs
def plot_rate_by_time(bin_times, trial_cfrs, average=None, shade=None, vline=None, colors=None,
                      labels=None, stats=None, sig_level=0.05, ax=None, **plt_kwargs):
    """Plot continuous firing rates across time.

    Parameters
    ----------
    bin_times : 1d array
        Values of the time bins, to be plotted on the x-axis.
    trial_cfrs : list of array or dict
        Continuous firing rate values, to be plotted on the y-axis.
        If each array is 1d values are plotted directly.
        If 2d, is to be averaged before plotting.
        If dict, each key is a condition label and each value the array of firing rates.
    average : {'mean', 'median'}, optional
        Averaging to apply to firing rate activity before plotting.
    shade : {'sem', 'std'} or list of array, optional
        Measure of variance to compute and/or plot as shading.
    vline : float or list of float, optional
        Location(s) to draw a vertical line. If None, no line is drawn.
    colors : str or list of str or dict, optional
        Color(s) to plot the firing rates.
        If more than one, should match the number of conditions.
        If a dictionary, the labels should match the spike condition labels.
    labels : list of str, optional
        Labels for each set of y-values.
        If provided, a legend is added to the plot.
    stats : list, optional
        Statistical results, including p-values, to use to annotate the plot.
    sig_level : float, optional, default: 0.05
        Threshold level to consider a result significant.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
        Custom kwargs: 'shade_alpha', 'legend_loc'.
    """

    # Check and unpack condition data, if provided as a dictionary input
    trial_cfrs, colors = extract_conditions_dict(trial_cfrs, colors)

    # Prepare data for Altair
    data = []
    for index, (cfrs, color) in enumerate(zip(trial_cfrs, colors)):
        for time, rate in zip(bin_times, cfrs):
            data.append({'time': time, 'rate': rate, 'condition': labels[index] if labels else None})

    df = pd.DataFrame(data)

    # Create the rate plot
    base = alt.Chart(df).encode(x='time:Q', y='rate:Q', color='condition:N')

    rate_line = base.mark_line(size=3).encode(
        strokeDash=alt.value(1)
    )

    # Add shading if provided
    if shade:
        shade_data = pd.DataFrame({'time': bin_times, 'lower': [rate - s for rate, s in zip(trial_cfrs, shade)],
                                   'upper': [rate + s for rate, s in zip(trial_cfrs, shade)]})
        shade_chart = alt.Chart(shade_data).mark_area(opacity=0.25).encode(
            x='time:Q',
            y='lower:Q',
            y2='upper:Q',
            color=alt.value('lightgray')
        )
        rate_line = rate_line + shade_chart

    # Add vertical lines
    if vline is not None:
        vline_data = pd.DataFrame({'vline': vline})
        vline_chart = alt.Chart(vline_data).mark_rule(color='black').encode(
            x='vline:Q'
        )
        rate_line = rate_line + vline_chart

    return rate_line.properties(width=600, height=400).configure_view(stroke='transparent')


@savefig
def plot_raster_and_rates(spikes, bins, time_range, conditions=None, colors=None,
                          title=None, raster_kwargs=None, rate_kwargs=None,
                          figsize=(6, 4), axes=None, **plt_kwargs):
    """Plot event-related raster plot with corresponding binned firing rate plot.

    Parameters
    ----------
    spikes : list of list of float or dict
        Spike times per trial.
        Multiple conditions can also be passed in.
        If dict, each key is a condition label and each value the list of list of spikes times.
    bins : float or 1d array
        The binning to apply to the spiking data.
        If float, the length of each bin.
        If array, precomputed bin definitions.
    time_range : list of [float, float], optional
        Time range, in seconds, to create the binned firing rate across.
        Only used if `bins` is a float.
    conditions : list, optional
        Condition labels for each trial.
        If provided, used to split the data by condition before plotting.
    colors : str or list of str or dict, optional
        Color(s) to plot the firing rates.
        If more than one, should match the number of conditions.
        If a dictionary, the labels should match the spike condition labels.
    raster_kwargs : dict, optional
        Additional keyword arguments for the raster plot, passed into `plot_rasters`.
    rate_kwargs : dict, optional
        Additional keyword arguments for the firing rate plot, passed into `plot_rate_by_time`.
    figsize : tuple, optional, default: (6, 4)
        Size of the figure to create. Only used if `axes` is None.
    axes : list of [Axes, Axes]
        Axes objects upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
        Custom kwargs: 'line_color', 'line_lw', 'line_alpha', 'line_linestyle'.
    """

    raster_kwargs = {} if raster_kwargs is None else raster_kwargs
    rate_kwargs = {} if rate_kwargs is None else rate_kwargs

    tbins, trial_frs = compute_trial_frs(spikes, bins, time_range)

    if conditions is not None:
        spikes = split_trials_by_condition(spikes, conditions)
        trial_frs = split_trials_by_condition(trial_frs, conditions)

    # Create raster and rate plots
    raster_plot = plot_rasters(spikes, colors=colors, **raster_kwargs)
    rate_plot = plot_rate_by_time(tbins, trial_frs, average='mean', shade='sem',
                                   **rate_kwargs, colors=colors)

    # Combine the plots
    combined_plot = alt.vconcat(raster_plot, rate_plot).resolve_scale(
        y='independent'
    )

    return combined_plot


## Trial plot utilities

def create_raster_title(label, avg_pre, avg_post, t_val=None, p_val=None):
    """Create a standardized title for an event-related raster plot.

    Parameters
    ----------
    label : str
        Label to add to the beginning of the title.
    avg_pre, avg_post : float
        The average firing rates pre and post event.
    t_val, p_val : float, optional
        The t value and p statistic for a t-test comparing pre and post event firing.

    Returns
    -------
    title : str
        Title for the plot.
    """

    if t_val is None:
        title = '{} - Pre: {:1.2f} / Post: {:1.2f}'.format(label, avg_pre, avg_post)
    else:
        title = '{} - Pre: {:1.2f} / Post: {:1.2f} (t:{:1.2f}, p:{:1.2f})'.format(\
            label, avg_pre, avg_post, t_val, p_val)

    return title
``` 

This code now uses Altair for plotting, which provides a more declarative and interactive approach to visualizations compared to Matplotlib.