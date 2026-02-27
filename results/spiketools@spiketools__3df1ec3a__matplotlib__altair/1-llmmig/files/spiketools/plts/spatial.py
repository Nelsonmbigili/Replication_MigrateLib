"""Plots for spatial measures and analyses."""

from copy import deepcopy
from itertools import repeat

import numpy as np
import altair as alt

from spiketools.utils.base import (listify, combine_dicts, relabel_keys,
                                   drop_key_prefix, subset_dict)
from spiketools.utils.checks import check_array_lst_orientation
from spiketools.utils.data import make_orientation, smooth_data, compute_range
from spiketools.modutils.functions import get_function_parameters
from spiketools.plts.annotate import add_dots, add_gridlines
from spiketools.plts.settings import DEFAULT_COLORS
from spiketools.plts.utils import savefig
from spiketools.plts.style import set_plt_kwargs

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_positions(position, spike_positions=None, landmarks=None, x_bins=None,
                   y_bins=None, invert=None, ax=None, **plt_kwargs):
    """Plot positions."""
    position = listify(position)
    orientation = check_array_lst_orientation(position)

    # Prepare base chart
    base = alt.Chart().mark_line().encode(
        x=alt.X('x:Q', scale=alt.Scale(reverse=(invert in ['x', 'both']))),
        y=alt.Y('y:Q', scale=alt.Scale(reverse=(invert in ['y', 'both']))),
        color=alt.value(plt_kwargs.pop('color', DEFAULT_COLORS[0])),
        opacity=alt.value(plt_kwargs.pop('alpha', 0.35))
    )

    # Add position data
    position_data = []
    for cur_position in position:
        x, y = make_orientation(cur_position, 'row', orientation)
        position_data.append({'x': x, 'y': y})
    position_chart = base.transform_calculate(data=position_data)

    # Add spike positions
    if spike_positions is not None:
        spike_data = []
        if isinstance(spike_positions, np.ndarray):
            x, y = make_orientation(spike_positions, 'row', orientation)
            spike_data.append({'x': x, 'y': y, 'color': 'red', 'opacity': 0.4})
        elif isinstance(spike_positions, dict):
            x, y = make_orientation(spike_positions.pop('positions'), 'row', orientation)
            spike_data.append({'x': x, 'y': y, **spike_positions})
        spike_chart = alt.Chart().mark_point().encode(
            x='x:Q', y='y:Q', color='color:N', opacity='opacity:Q'
        ).transform_calculate(data=spike_data)
        position_chart += spike_chart

    # Add landmarks
    if landmarks is not None:
        landmark_data = []
        landmarks = deepcopy(landmarks)
        if isinstance(landmarks, np.ndarray):
            x, y = make_orientation(landmarks, 'row', orientation)
            landmark_data.append({'x': x, 'y': y, 'opacity': 0.85})
        elif isinstance(landmarks, dict):
            x, y = make_orientation(landmarks.pop('positions'), 'row', orientation)
            landmark_data.append({'x': x, 'y': y, **landmarks})
        landmark_chart = alt.Chart().mark_point().encode(
            x='x:Q', y='y:Q', opacity='opacity:Q'
        ).transform_calculate(data=landmark_data)
        position_chart += landmark_chart

    # Add gridlines
    if x_bins or y_bins:
        gridlines = []
        if x_bins:
            for x in x_bins:
                gridlines.append({'x': x, 'y': None})
        if y_bins:
            for y in y_bins:
                gridlines.append({'x': None, 'y': y})
        gridline_chart = alt.Chart().mark_rule().encode(
            x='x:Q', y='y:Q'
        ).transform_calculate(data=gridlines)
        position_chart += gridline_chart

    return position_chart


@savefig
@set_plt_kwargs
def plot_position_1d(position, events=None, colors=None, sizes=None, ax=None, **plt_kwargs):
    """Position 1d position data, with annotated events."""
    position_chart = alt.Chart().mark_line().encode(
        x=alt.X('index:Q', title='Position'),
        y=alt.Y('value:Q', title=None),
        color=alt.value(plt_kwargs.pop('position_color', DEFAULT_COLORS[0])),
        opacity=alt.value(plt_kwargs.pop('position_alpha', 0.35))
    ).transform_calculate(data=[{'index': i, 'value': pos} for i, pos in enumerate(position)])

    # Add events
    if events is not None:
        event_data = []
        events = [events] if isinstance(events, (dict, np.ndarray)) else events
        for event in events:
            if isinstance(event, np.ndarray):
                for e in event:
                    event_data.append({'x': e, 'color': next(colors), 'size': next(sizes)})
            elif isinstance(event, dict):
                event_data.append(event)
        event_chart = alt.Chart().mark_rule().encode(
            x='x:Q', color='color:N', size='size:Q'
        ).transform_calculate(data=event_data)
        position_chart += event_chart

    return position_chart


@savefig
@set_plt_kwargs
def plot_heatmap(data, smooth=False, smoothing_kernel=1.5, ignore_zero=False,
                 cbar=False, cmap=None, vmin=None, vmax=None,
                 transpose=False, invert=None, ax=None, **plt_kwargs):
    """Plot a spatial heat map."""
    if transpose:
        data = data.T
    if smooth:
        data = smooth_data(data, smoothing_kernel)
    if ignore_zero:
        data = deepcopy(data)
        data[data == 0.] = np.nan

    heatmap_chart = alt.Chart().mark_rect().encode(
        x=alt.X('x:O', scale=alt.Scale(reverse=(invert in ['x', 'both']))),
        y=alt.Y('y:O', scale=alt.Scale(reverse=(invert in ['y', 'both']))),
        color=alt.Color('value:Q', scale=alt.Scale(domain=[vmin, vmax], scheme=cmap))
    ).transform_calculate(data=[{'x': i, 'y': j, 'value': val}
                                for i, row in enumerate(data)
                                for j, val in enumerate(row)])

    if cbar:
        heatmap_chart += heatmap_chart.encode(color=alt.Color('value:Q', legend=None))

    return heatmap_chart
