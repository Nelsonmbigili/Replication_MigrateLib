"""Plots for spatial measures and analyses."""

from copy import deepcopy
from itertools import repeat

import numpy as np
import seaborn as sns

from spiketools.utils.base import (listify, combine_dicts, relabel_keys,
                                   drop_key_prefix, subset_dict)
from spiketools.utils.checks import check_array_lst_orientation
from spiketools.utils.data import make_orientation, smooth_data, compute_range
from spiketools.modutils.functions import get_function_parameters
from spiketools.plts.annotate import add_dots
from spiketools.plts.settings import DEFAULT_COLORS
from spiketools.plts.utils import check_ax, make_axes, savefig
from spiketools.plts.style import set_plt_kwargs, invert_axes

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_positions(position, spike_positions=None, landmarks=None, x_bins=None,
                   y_bins=None, invert=None, ax=None, **plt_kwargs):
    """Plot positions.

    Parameters
    ----------
    position : 2d array or list of 2d array
        Position data.
        If a list, each array from the list is plotted separately, on the same plot.
    spike_positions : 2d array or dict, optional
        Position values of spikes, to indicate on the plot.
        If array, defines the positions.
        If dictionary, should include a 'positions' key plus additional plot arguments.
    landmarks : 1d or 2d array or dict or list, optional
        Position values of landmarks, to be added to the plot.
        If array, defines the positions, as [x, y] for a single landmark 1d array,
        or as [[x-pos], [y-pos]] for a 2d definition of multiple landmarks.
        If dictionary, should include a 'positions' key with an array plus additional arguments.
        Multiple landmarks can be added by passing a list of arrays or a list of dictionaries.
    x_bins, y_bins : list of float, optional
        Bin edges for each axis.
        If provided, these are used to draw grid lines on the plot.
    invert : {'x', 'y', 'both'}, optional
        If provided, inverts the plot axes over x, y or both axes.
        Note that invert x is equivalent to flipping the data left/right, and y to flipping up/down.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    orientation = check_array_lst_orientation(listify(position))
    for cur_position in listify(position):
        sns.lineplot(x=make_orientation(cur_position, 'row', orientation)[0],
                     y=make_orientation(cur_position, 'row', orientation)[1],
                     ax=ax, color=plt_kwargs.pop('color', DEFAULT_COLORS[0]),
                     alpha=plt_kwargs.pop('alpha', 0.35), **plt_kwargs)

    if spike_positions is not None:
        defaults = {'color': 'red', 'alpha': 0.4, 's': 36}
        if isinstance(spike_positions, np.ndarray):
            sns.scatterplot(x=make_orientation(spike_positions, 'row', orientation)[0],
                            y=make_orientation(spike_positions, 'row', orientation)[1],
                            ax=ax, **defaults)
        elif isinstance(spike_positions, dict):
            sns.scatterplot(x=make_orientation(spike_positions.pop('positions'), 'row', orientation)[0],
                            y=make_orientation(spike_positions.pop('positions'), 'row', orientation)[1],
                            ax=ax, **{**defaults, **spike_positions})

    if landmarks is not None:
        landmarks = deepcopy(landmarks)
        defaults = {'alpha': 0.85, 's': 144}
        for landmark in [landmarks] if not isinstance(landmarks, list) else landmarks:
            if isinstance(landmark, np.ndarray):
                sns.scatterplot(x=make_orientation(landmark, 'row', orientation)[0],
                                y=make_orientation(landmark, 'row', orientation)[1],
                                ax=ax, **defaults)
            elif isinstance(landmark, dict):
                sns.scatterplot(x=make_orientation(landmark.pop('positions'), 'row', orientation)[0],
                                y=make_orientation(landmark.pop('positions'), 'row', orientation)[1],
                                ax=ax, **landmark)

    invert_axes(invert, ax)


@savefig
@set_plt_kwargs
def plot_position_1d(position, events=None, colors=None, sizes=None, ax=None, **plt_kwargs):
    """Position 1d position data, with annotated events."""

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if position is not None:
        sns.lineplot(x=np.arange(len(position)), y=position, ax=ax,
                     color=plt_kwargs.pop('position_color', DEFAULT_COLORS[0]),
                     alpha=plt_kwargs.pop('position_alpha', 1.0),
                     linewidth=plt_kwargs.pop('position_linewidth', 1.5))

    colors = iter(listify(colors)) if colors else iter(DEFAULT_COLORS[1:])
    sizes = iter(listify(sizes)) if sizes else repeat(1)

    events = [events] if isinstance(events, (dict, np.ndarray)) else events
    for event in events:
        if isinstance(event, np.ndarray):
            sns.scatterplot(x=event, y=[1] * len(event), ax=ax,
                            color=next(colors), s=next(sizes) * 10, **plt_kwargs)
        elif isinstance(event, dict):
            sns.scatterplot(x=event['positions'], y=[1] * len(event['positions']), ax=ax,
                            color=event.get('color', next(colors)),
                            s=event.get('size', next(sizes)) * 10, **plt_kwargs)

    ax.set(xlabel='Position', yticks=[])


@savefig
@set_plt_kwargs
def plot_heatmap(data, smooth=False, smoothing_kernel=1.5, ignore_zero=False,
                 cbar=False, cmap=None, vmin=None, vmax=None,
                 transpose=False, invert=None, ax=None, **plt_kwargs):
    """Plot a spatial heat map."""

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if data.ndim < 2:
        data = np.atleast_2d(data)

    if transpose:
        data = data.T

    if smooth:
        data = smooth_data(data, smoothing_kernel)

    if ignore_zero:
        data = deepcopy(data)
        data[data == 0.] = np.nan

    sns.heatmap(data, ax=ax, cmap=cmap, vmin=vmin, vmax=vmax,
                cbar=cbar, cbar_kws={'shrink': 0.8}, **plt_kwargs)

    ax.set(xticks=[], yticks=[])
    ax.set_axis_off()

    invert_axes(invert, ax)
