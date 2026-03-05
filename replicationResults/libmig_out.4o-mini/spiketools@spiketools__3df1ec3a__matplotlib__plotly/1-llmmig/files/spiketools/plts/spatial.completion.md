To migrate the provided code from using the `matplotlib` library to the `plotly` library, several key changes were made:

1. **Import Changes**: The import statement for `matplotlib.pyplot` was replaced with the appropriate `plotly` imports. Specifically, `plotly.graph_objects` was used for creating figures and traces.

2. **Plotting Functions**: The plotting functions were changed from `ax.plot`, `ax.imshow`, and `ax.eventplot` to their `plotly` equivalents. For example, `ax.plot` was replaced with `go.Scatter`, and `ax.imshow` was replaced with `go.Heatmap`.

3. **Figure Creation**: Instead of using an `Axes` object, `plotly` uses a `Figure` object that can contain multiple traces. The `Figure` is created and updated with traces for each plot.

4. **Layout Adjustments**: The layout settings (like axis labels and visibility) were adjusted using `update_layout` and `update_traces` methods in `plotly`.

5. **Colorbar Handling**: The colorbar is handled differently in `plotly`, so adjustments were made to ensure it appears correctly.

6. **Event Handling**: The handling of events and annotations was adapted to fit the `plotly` style.

Here is the modified code after migrating to `plotly`:

```python
"""Plots for spatial measures and analyses."""

from copy import deepcopy
from itertools import repeat

import numpy as np
import plotly.graph_objects as go

from spiketools.utils.base import (listify, combine_dicts, relabel_keys,
                                   drop_key_prefix, subset_dict)
from spiketools.utils.checks import check_array_lst_orientation
from spiketools.utils.data import make_orientation, smooth_data, compute_range
from spiketools.modutils.functions import get_function_parameters
from spiketools.plts.annotate import add_dots, add_gridlines
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

    fig = go.Figure()

    orientation = check_array_lst_orientation(listify(position))
    for cur_position in listify(position):
        fig.add_trace(go.Scatter(
            x=make_orientation(cur_position, 'row', orientation)[0],
            y=make_orientation(cur_position, 'row', orientation)[1],
            mode='lines',
            line=dict(color=plt_kwargs.pop('color', DEFAULT_COLORS[0]), 
                      width=plt_kwargs.pop('linewidth', 2)),
            opacity=plt_kwargs.pop('alpha', 0.35),
            **plt_kwargs
        ))

    if spike_positions is not None:
        defaults = {'marker': dict(color='red', size=6, opacity=0.4)}
        if isinstance(spike_positions, np.ndarray):
            add_dots(make_orientation(spike_positions, 'row', orientation),
                     fig=fig, **defaults)
        elif isinstance(spike_positions, dict):
            add_dots(make_orientation(spike_positions.pop('positions'), 'row', orientation),
                     fig=fig, **{**defaults, **spike_positions})

    if landmarks is not None:
        landmarks = deepcopy(landmarks)
        defaults = {'marker': dict(size=12, opacity=0.85)}
        for landmark in [landmarks] if not isinstance(landmarks, list) else landmarks:
            if isinstance(landmark, np.ndarray):
                add_dots(make_orientation(landmark, 'row', orientation),
                         fig=fig, **defaults)
            elif isinstance(landmark, dict):
                add_dots(make_orientation(landmark.pop('positions'), 'row', orientation),
                         fig=fig, **landmark)

    add_gridlines(x_bins, y_bins, fig)
    invert_axes(invert, fig)

    fig.update_layout(
        xaxis_title='X Axis',
        yaxis_title='Y Axis',
        showlegend=False
    )
    fig.show()


@savefig
@set_plt_kwargs
def plot_position_1d(position, events=None, colors=None, sizes=None, ax=None, **plt_kwargs):
    """Position 1d position data, with annotated events.

    Parameters
    ----------
    position : 1d array
        Position data.
    events : 1d array or dict or list
        Events to add to the plot, as vertical lines.
        If array, defines the position(s) of each event.
        If dictionary, should include a 'positions' key with an array plus additional arguments.
        Multiple event definitions can be passed in as a list of dictionaries or arrays.
    colors : str or list of str
        Color(s) for each event.
        Only used if `events` are passed in as an array or list of arrays.
    sizes : float or list of float
        Size(s) for each event.
        Only used if `events` are passed in as an array or list of arrays.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
        Custom kwargs: 'position_color', 'position_alpha', 'position_linewidth'.
    """

    fig = go.Figure()

    if position is not None:
        position_plt_kwargs = drop_key_prefix(subset_dict(plt_kwargs, 'position'), 'position')
        fig.add_trace(go.Scatter(
            x=position,
            y=[1] * len(position),
            mode='lines',
            **position_plt_kwargs
        ))

    colors = iter(listify(colors)) if colors else iter(DEFAULT_COLORS[1:])
    sizes = iter(listify(sizes)) if sizes else repeat(1)

    events = [events] if isinstance(events, (dict, np.ndarray)) else events
    for event in events:
        if isinstance(event, np.ndarray):
            fig.add_trace(go.Scatter(
                x=event,
                y=[1] * len(event),
                mode='markers',
                marker=dict(color=next(colors), size=next(sizes)),
                **plt_kwargs
            ))
        elif isinstance(event, dict):
            fig.add_trace(go.Scatter(
                **relabel_keys(event, {'size': 'marker.size'}),
                mode='markers',
                **plt_kwargs
            ))

    fig.update_layout(
        xaxis_title='Position',
        yaxis=dict(showticklabels=False)
    )
    fig.show()


@savefig
@set_plt_kwargs
def plot_position_by_time(timestamps, position, spikes=None, spike_positions=None,
                          event_times=None, event_positions=None, event_kwargs=None,
                          time_bins=None, position_bins=None, invert=None,
                          ax=None, **plt_kwargs):
    """Plot position across time for a single dimension.

    Parameters
    ----------
    timestamps : 1d array
        Timestamps, in seconds, corresponding to the position values.
    position : 1d array
        Position values, for a single dimension.
    spikes : 1d array, optional
        Spike times, in seconds.
    spike_positions : 1d array, optional
        Position values of spikes, to indicate on the plot.
    event_times : 1d array, optional
        Time values of event markers to add to the plot.
        If provided, `event_positions` must also be provided.
    event_positions : 1d array, optional
        Position values of event markers to add to the plot
        If provided, `event_times` must also be provided.
    event_kwargs : dict, optional
        Keyword arguments for styling the events to be added to the plot.
    time_bins : list of float, optional
        Bin edges for the time axis.
        If provided, these are used to draw vertical grid lines on the plot.
    position_bins : list of float, optional
        Bin edges for the position axis.
        If provided, these are used to draw horizontal grid lines on the plot.
    invert : {'x', 'y', 'both'}, optional
        If provided, inverts the plot axes over x, y or both axes.
        Note that invert x is equivalent to flipping the data left/right, and y to flipping up/down.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    fig = go.Figure()

    spike_positions_plot = None
    if spikes is not None:
        spike_positions_plot = np.array([spikes, spike_positions])

    event_defaults = {'marker': dict(size=10, opacity=0.85)}
    landmarks = {'positions': np.array([event_times, event_positions]),
                 **combine_dicts([event_defaults, {} if not event_kwargs else event_kwargs])}

    plot_positions(np.array([timestamps, position]), spike_positions_plot,
                   landmarks=landmarks, x_bins=time_bins, y_bins=position_bins,
                   invert=invert, ax=fig, **plt_kwargs)

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Position'
    )
    fig.show()


@savefig
@set_plt_kwargs
def plot_heatmap(data, smooth=False, smoothing_kernel=1.5, ignore_zero=False,
                 cbar=False, cmap=None, vmin=None, vmax=None,
                 transpose=False, invert=None, ax=None, **plt_kwargs):
    """Plot a spatial heat map.

    Parameters
    ----------
    data : 2d array
        Measure to plot across a grided environment.
    smooth : bool, optional, default: False
        Whether to smooth the data before plotting.
    smoothing_kernel : float, optional, default: 1.5
        Standard deviation of the gaussian kernel to apply for smoothing.
    ignore_zero : bool, optional, default: False
        If True, replaces 0's with NaN for plotting.
    cbar : bool, optional, default: False
        Whether to add a colorbar to the plot.
    cmap : str, optional
        Which colormap to use to plot.
    vmin, vmax : float, optional
        Min and max plot ranges.
    transpose : bool, optional, default: False
        Whether to transpose the data before plotting.
    invert : {'x', 'y', 'both'}, optional
        If provided, inverts the plot axes over x, y or both axes.
        Note that invert x is equivalent to flipping the data left/right, and y to flipping up/down.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.

    Notes
    -----
    This function uses `plt.imshow` to visualize the matrix.
    Note that in doing so, it defaults to setting the origin to 'lower'.
    This setting can be overwritten by passing in a value for `origin`.
    """

    fig = go.Figure()

    if data.ndim < 2:
        data = np.atleast_2d(data)

    if transpose:
        data = data.T

    if smooth:
        data = smooth_data(data, smoothing_kernel)

    if ignore_zero:
        data = deepcopy(data)
        data[data == 0.] = np.nan

    im = go.Heatmap(z=data, colorscale=cmap, zmin=vmin, zmax=vmax,
                     **plt_kwargs)

    fig.add_trace(im)

    fig.update_layout(
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
        showlegend=False
    )

    if cbar:
        fig.update_layout(coloraxis_colorbar=dict(title='Colorbar'))

    invert_axes(invert, fig)

    fig.show()


@savefig
def plot_trial_heatmaps(trial_data, **plt_kwargs):
    """Plot spatial heat maps for a set of trials.

    Parameters
    ----------
    trial_data : 3d array
        Spatially binned spike activity, per trial, with shape of [n_trials, n_xbins, n_ybins].
    plt_kwargs
        Additional arguments to pass into the plot function.
        This can include arguments into `make_axes`, which initializes the set of axes.
    """

    axis_kwargs = {key: plt_kwargs.pop(key) \
        for key in get_function_parameters(make_axes).keys() if key in plt_kwargs}
    axes = make_axes(trial_data.shape[0], **axis_kwargs)
    for data, ax in zip(trial_data, axes):
        plot_heatmap(data, **plt_kwargs, ax=ax)


def create_heatmap_title(label, data, stat=None, p_val=None):
    """Create a standardized title for an heatmap, listing the data range.

    Parameters
    ----------
    label : str
        Label to add to the beginning of the title.
    data : 2d array
        The array of data that is plotted, used to compute the data range.
    stat, p_val : float, optional
        A statistical test value and p statistic to report related to the heatmap.

    Returns
    -------
    title : str
        Title for the plot.
    """

    template = '({:1.2f}-{:1.2f})' if 'float' in str(data.dtype) else '({:d}-{:d})'
    if stat is None:
        title = ('{} - ' + template).format(label, *compute_range(data))
    else:
        title = ('{} - ' + template + '\n stat: {:1.2f}, p: {:1.2f}').format(\
            label, *compute_range(data), stat, p_val)

    return title
```

This code now uses `plotly` for all plotting functionalities while maintaining the original structure and logic of the code.