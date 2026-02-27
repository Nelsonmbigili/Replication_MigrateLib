"""Plots for trial related measures and analyses."""

import numpy as np
import pandas as pd
import altair as alt

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
    """Plot rasters across multiple trials using Altair.

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
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Check and unpack condition data, if provided as a dictionary input
    spikes, colors = extract_conditions_dict(spikes, colors)

    # Flatten data for plotting
    trial_ids = []
    spike_times = []
    for trial_idx, trial_spikes in enumerate(spikes):
        trial_ids.extend([trial_idx] * len(trial_spikes))
        spike_times.extend(trial_spikes)

    # Create a DataFrame for Altair
    data = pd.DataFrame({'Trial': trial_ids, 'Spike Time': spike_times})

    # Create the raster plot
    raster = alt.Chart(data).mark_tick().encode(
        x='Spike Time:Q',
        y=alt.Y('Trial:O', axis=None if not show_axis else alt.Axis()),
        color=alt.value(colors[0] if isinstance(colors, list) else 'black')
    )

    # Add vertical lines if specified
    if vline is not None:
        vline = [vline] if isinstance(vline, (float, int)) else vline
        vline_data = pd.DataFrame({'vline': vline})
        vlines = alt.Chart(vline_data).mark_rule(color='green').encode(
            x='vline:Q'
        )
        raster = raster + vlines

    # Add shaded regions if specified
    if vshade is not None:
        vshade = [vshade] if isinstance(vshade[0], (float, int)) else vshade
        vshade_data = pd.DataFrame({'start': [v[0] for v in vshade], 'end': [v[1] for v in vshade]})
        vshades = alt.Chart(vshade_data).mark_rect(opacity=0.25, color='red').encode(
            x='start:Q',
            x2='end:Q'
        )
        raster = raster + vshades

    return raster


@set_plt_kwargs
def plot_rate_by_time(bin_times, trial_cfrs, average=None, shade=None, vline=None, colors=None,
                      labels=None, stats=None, sig_level=0.05, **plt_kwargs):
    """Plot continuous firing rates across time using Altair.

    Parameters
    ----------
    bin_times : 1d array
        Values of the time bins, to be plotted on the x-axis.
    trial_cfrs : list of array or dict
        Continuous firing rate values, to be plotted on the y-axis.
    average : {'mean', 'median'}, optional
        Averaging to apply to firing rate activity before plotting.
    shade : {'sem', 'std'} or list of array, optional
        Measure of variance to compute and/or plot as shading.
    vline : float or list of float, optional
        Location(s) to draw a vertical line. If None, no line is drawn.
    colors : str or list of str or dict, optional
        Color(s) to plot the firing rates.
    labels : list of str, optional
        Labels for each set of y-values.
    stats : list, optional
        Statistical results, including p-values, to use to annotate the plot.
    sig_level : float, optional, default: 0.05
        Threshold level to consider a result significant.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Check and unpack condition data, if provided as a dictionary input
    trial_cfrs, colors = extract_conditions_dict(trial_cfrs, colors)

    # Compute averages and variance if specified
    if isinstance(average, str):
        trial_cfrs = [get_avg_func(average)(arr, 0) for arr in trial_cfrs]
    if isinstance(shade, str):
        shade = [get_var_func(shade)(arr, 0) for arr in trial_cfrs]

    # Create a DataFrame for Altair
    data = pd.DataFrame({
        'Time': np.tile(bin_times, len(trial_cfrs)),
        'Firing Rate': np.concatenate(trial_cfrs),
        'Condition': np.repeat(labels if labels else range(len(trial_cfrs)), len(bin_times))
    })

    # Create the line plot
    line = alt.Chart(data).mark_line().encode(
        x='Time:Q',
        y='Firing Rate:Q',
        color='Condition:N'
    )

    # Add shaded regions if specified
    if shade:
        shade_data = pd.DataFrame({
            'Time': np.tile(bin_times, len(trial_cfrs)),
            'Lower': np.concatenate([y - s for y, s in zip(trial_cfrs, shade)]),
            'Upper': np.concatenate([y + s for y, s in zip(trial_cfrs, shade)]),
            'Condition': np.repeat(labels if labels else range(len(trial_cfrs)), len(bin_times))
        })
        shaded = alt.Chart(shade_data).mark_area(opacity=0.25).encode(
            x='Time:Q',
            y='Lower:Q',
            y2='Upper:Q',
            color='Condition:N'
        )
        line = line + shaded

    # Add vertical lines if specified
    if vline is not None:
        vline = [vline] if isinstance(vline, (float, int)) else vline
        vline_data = pd.DataFrame({'vline': vline})
        vlines = alt.Chart(vline_data).mark_rule(color='black').encode(
            x='vline:Q'
        )
        line = line + vlines

    return line
