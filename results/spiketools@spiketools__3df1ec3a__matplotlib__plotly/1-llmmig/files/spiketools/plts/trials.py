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
