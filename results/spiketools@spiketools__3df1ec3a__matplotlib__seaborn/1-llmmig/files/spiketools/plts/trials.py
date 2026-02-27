"""Plots for trial related measures and analyses."""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    # Check and unpack condition data, if provided as a dictionary input
    spikes, colors = extract_conditions_dict(spikes, colors)

    # Flatten data for plotting
    spikes = flatten(spikes)
    colors = DEFAULT_COLORS[:len(spikes)] if not colors else colors

    # Plot raster using seaborn's rugplot
    for trial_idx, trial_spikes in enumerate(spikes):
        sns.rugplot(trial_spikes, ax=ax, height=0.5, color=colors[trial_idx % len(colors)])

    # If provided, add events to plot
    if events is not None:
        for trial_idx, trial_events in enumerate(events):
            sns.rugplot(trial_events, ax=ax, height=0.8, color='red', linewidth=2)

    # Add vertical lines and shaded regions
    add_vlines(vline, ax, zorder=0, color='green', lw=2.5, alpha=0.5)
    add_vshades(vshade, ax, color='red', alpha=0.25)

    if not show_axis:
        ax.set_axis_off()


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
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    # Check and unpack condition data, if provided as a dictionary input
    trial_cfrs, colors = extract_conditions_dict(trial_cfrs, colors)

    # If not a list of arrays, embed in a list to allow for looping (to support multiple inputs)
    if not isinstance(trial_cfrs[0], np.ndarray):
        trial_cfrs = [trial_cfrs]

    colors = DEFAULT_COLORS[:len(trial_cfrs)] if not colors else colors

    # Compute shading if requested
    if isinstance(shade, str):
        shade = [get_var_func(shade)(arr, 0) for arr in trial_cfrs]

    # Compute averages if requested
    if isinstance(average, str):
        trial_cfrs = [get_avg_func(average)(arr, 0) for arr in trial_cfrs]

    # Plot firing rates using seaborn
    for ind, (ys, color) in enumerate(zip(trial_cfrs, colors)):
        sns.lineplot(x=bin_times, y=ys, ax=ax, color=color,
                     label=labels[ind] if labels else None, ci='sd' if shade else None)

    ax.set(xlabel='Time (s)', ylabel='Firing Rate (Hz)')

    # Add vertical lines
    add_vlines(vline, ax, zorder=0, color='black', linestyle='--', lw=2.0, alpha=0.5)

    if labels:
        ax.legend(loc='best')

    if stats:
        add_significance(stats, sig_level=sig_level, ax=ax)
