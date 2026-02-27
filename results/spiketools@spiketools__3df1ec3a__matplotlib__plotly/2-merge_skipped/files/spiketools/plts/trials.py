"""Plots for trial related measures and analyses."""

import numpy as np
import plotly.graph_objects as go

from spiketools.measures.trials import compute_trial_frs
from spiketools.utils.base import flatten
from spiketools.utils.trials import extract_conditions_dict
from spiketools.utils.trials import split_trials_by_condition
from spiketools.utils.options import get_avg_func, get_var_func
from spiketools.plts.settings import DEFAULT_COLORS
from spiketools.plts.annotate import add_significance
from spiketools.plts.utils import get_kwargs
from spiketools.plts.style import set_plt_kwargs

###################################################################################################
###################################################################################################

@set_plt_kwargs
def plot_rasters(spikes, events=None, vline=None, colors=None, vshade=None,
                 show_axis=False, **plt_kwargs):
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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))
    """Plot rasters across multiple trials using Plotly."""

    custom_kwargs = ['line_color', 'line_lw', 'line_alpha',
                     'shade_color', 'shade_alpha',
                     'event_color', 'event_linewidths', 'event_linelengths']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    # Check and unpack condition data, if provided as a dictionary input
    spikes, colors = extract_conditions_dict(spikes, colors)

    # This process infers whether there are embedded lists of multiple conditions
    check = False
    for val in spikes:
        try:
            if isinstance(val, float):
                break
            elif isinstance(val[0], (list, np.ndarray)):
                check = True
                break
        except (IndexError, TypeError):
            continue

    # If multiple conditions, organize colors across trials, and flatten data for plotting
    if check:
        lens = [len(el) for el in spikes]
        colors = DEFAULT_COLORS[0:len(lens)] if not colors else colors
        colors = flatten([[col] * ll for col, ll in zip(colors, lens)])
        spikes = flatten(spikes)

    # Create the figure
    fig = go.Figure()

    # Add spike raster data
    for trial_idx, trial_spikes in enumerate(spikes):
        fig.add_trace(go.Scatter(
            x=trial_spikes,
            y=[trial_idx] * len(trial_spikes),
            mode='markers',
            marker=dict(color=colors[trial_idx] if colors else 'black'),
            name=f'Trial {trial_idx + 1}'
        ))

    # Add events if provided
    if events is not None:
        for trial_idx, trial_events in enumerate(events):
            fig.add_trace(go.Scatter(
                x=trial_events,
                y=[trial_idx] * len(trial_events),
                mode='markers',
                marker=dict(color=custom_plt_kwargs.pop('event_color', 'red')),
                name=f'Event {trial_idx + 1}'
            ))

    # Add vertical lines
    if vline is not None:
        vline = [vline] if isinstance(vline, (float, int)) else vline
        for line in vline:
            fig.add_shape(
                type="line",
                x0=line, x1=line,
                y0=0, y1=len(spikes),
                line=dict(color=custom_plt_kwargs.pop('line_color', 'green'),
                          width=custom_plt_kwargs.pop('line_lw', 2.5),
                          dash='dash')
            )

    # Add vertical shading
    if vshade is not None:
        vshade = [vshade] if isinstance(vshade[0], (float, int)) else vshade
        for shade in vshade:
            fig.add_shape(
                type="rect",
                x0=shade[0], x1=shade[1],
                y0=0, y1=len(spikes),
                fillcolor=custom_plt_kwargs.pop('shade_color', 'red'),
                opacity=custom_plt_kwargs.pop('shade_alpha', 0.25),
                line_width=0
            )

    # Update layout
    fig.update_layout(
        showlegend=False,
        xaxis=dict(title='Time (s)', showgrid=False),
        yaxis=dict(title='Trials', showgrid=False),
    )
    if not show_axis:
        fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))

    fig.show()


@set_plt_kwargs
def plot_rate_by_time(bin_times, trial_cfrs, average=None, shade=None, vline=None, colors=None,
                      labels=None, stats=None, sig_level=0.05, **plt_kwargs):
    """Plot continuous firing rates across time using Plotly."""

    custom_kwargs = ['shade_alpha', 'legend_loc', 'line_color', 'line_lw', 'line_alpha']
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

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    custom_kwargs = ['shade_alpha', 'legend_loc','line_color', 'line_lw', 'line_alpha']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    # Check and unpack condition data, if provided as a dictionary input
    trial_cfrs, colors = extract_conditions_dict(trial_cfrs, colors)

    # If not a list of arrays, embed in a list to allow for looping (to support multiple inputs)
    if not isinstance(trial_cfrs[0], np.ndarray):
        trial_cfrs = [trial_cfrs]
    if isinstance(trial_cfrs, np.ndarray) and trial_cfrs.ndim == 2 and isinstance(average, str):
        trial_cfrs = [trial_cfrs]

    colors = DEFAULT_COLORS[0:len(trial_cfrs)] if not colors else colors
    colors = [colors] if isinstance(colors, str) else colors

    if isinstance(shade, str):
        shade = [get_var_func(shade)(arr, 0) for arr in trial_cfrs]

    if isinstance(average, str):
        trial_cfrs = [get_avg_func(average)(arr, 0) for arr in trial_cfrs]

    # Create the figure
    fig = go.Figure()

    # Add firing rate data
    for ind, (ys, color) in enumerate(zip(trial_cfrs, colors)):
        fig.add_trace(go.Scatter(
            x=bin_times,
            y=ys,
            mode='lines',
            line=dict(color=color, width=plt_kwargs.pop('lw', 3)),
            name=labels[ind] if labels else f'Condition {ind + 1}'
        ))

        if shade:
            fig.add_trace(go.Scatter(
                x=np.concatenate([bin_times, bin_times[::-1]]),
                y=np.concatenate([ys - shade[ind], (ys + shade[ind])[::-1]]),
                fill='toself',
                fillcolor=color,
                opacity=custom_plt_kwargs.pop('shade_alpha', 0.25),
                line=dict(width=0),
                showlegend=False
            ))

    # Add vertical lines
    if vline is not None:
        vline = [vline] if isinstance(vline, (float, int)) else vline
        for line in vline:
            fig.add_shape(
                type="line",
                x0=line, x1=line,
                y0=0, y1=max([max(ys) for ys in trial_cfrs]),
                line=dict(color=custom_plt_kwargs.pop('line_color', 'black'),
                          width=custom_plt_kwargs.pop('line_lw', 2.0),
                          dash='dash')
            )

    # Update layout
    fig.update_layout(
        xaxis=dict(title='Time (s)'),
        yaxis=dict(title='Firing Rate (Hz)'),
        legend=dict(title='Conditions', x=1.05, y=1),
    )

    fig.show()
    if labels:
        ax.legend(loc=custom_plt_kwargs.pop('legend_loc', 'best'))

    if stats:
        add_significance(stats, sig_level=sig_level, ax=ax)


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

    custom_kwargs = ['line_color', 'line_lw', 'line_alpha', 'line_linestyle']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    raster_kwargs = {} if raster_kwargs is None else raster_kwargs
    rate_kwargs = {} if rate_kwargs is None else rate_kwargs

    tbins, trial_frs = compute_trial_frs(spikes, bins, time_range)

    if conditions is not None:
        spikes = split_trials_by_condition(spikes, conditions)
        trial_frs = split_trials_by_condition(trial_frs, conditions)

    if not axes:
        axes = make_axes(2, 1, sharex=True, hspace=0.0, figsize=figsize)

    plot_rasters(spikes, title=title, colors=colors, **raster_kwargs, ax=axes[0])

    plot_rate_by_time(tbins, trial_frs, average='mean', shade='sem',
                      **rate_kwargs, colors=colors, ax=axes[1])
    for side in ['right', 'top']:
        axes[1].spines[side].set_visible(False)

    # Add vertical line across axes
    line_kwargs = {
        'color' : custom_plt_kwargs.pop('line_color', 'green'),
        'lw' : custom_plt_kwargs.pop('line_lw', 2.5),
        'alpha' : custom_plt_kwargs.pop('line_alpha', 0.5),
        'linestyle' : custom_plt_kwargs.pop('line_linestyle', '--'),
    }
    axes[0].axvline(0, -1.25, 1, **line_kwargs, clip_on=False)
    axes[1].axvline(0, 0, 1, **line_kwargs, clip_on=False)


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