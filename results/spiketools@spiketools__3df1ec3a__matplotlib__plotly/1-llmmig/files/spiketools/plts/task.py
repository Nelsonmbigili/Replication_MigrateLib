"""Plots for tasks and task structure related visualizations."""

import numpy as np
import plotly.graph_objects as go

from spiketools.utils.base import listify
from spiketools.plts.utils import savefig
from spiketools.plts.settings import DEFAULT_COLORS

###################################################################################################
###################################################################################################

@savefig
def plot_task_structure(task_ranges=None, event_lines=None, data_points=None,
                        range_colors=None, line_colors=None, range_kwargs=None, line_kwargs=None,
                        fig=None, **plt_kwargs):
    """Plot task structure with shaded ranges of event durations and lines for point events.

    Parameters
    ----------
    task_ranges : list of list of float, optional
        List of start and end ranges to shade in, to indicate event durations.
        To add multiple different shaded regions, pass a list of multiple shade definitions.
    event_lines : list of float, optional
        Timestamps at which to draw vertical lines, to indicate point events.
        To add multiple different lines, pass a list of multiple line definitions.
    data_points : 1d array, optional
        Set of timestamps to indicate data points of interest on the plot.
    range_colors : list of str, optional
        Colors to plot the ranges in. Used if passing multiple task range sections.
    line_colors : list of str, optional
        Colors to plot the lines in. Used if passing multiple line sections.
    range_kwargs : dict, optional
        Additional keyword arguments for the range shades.
    line_kwargs : dict, optional
        Additional keyword arguments for the event lines.
    fig : go.Figure, optional
        Plotly figure object to add elements to.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Create a new figure if one is not provided
    if fig is None:
        fig = go.Figure()

    range_kwargs = {} if range_kwargs is None else range_kwargs
    line_kwargs = {} if line_kwargs is None else line_kwargs

    # Add shaded ranges
    if task_ranges is not None:
        if not isinstance(task_ranges[0][0], (int, float, np.int64, np.float64)):
            for trange, color in zip(task_ranges, range_colors if range_colors else DEFAULT_COLORS):
                range_kwargs['fillcolor'] = color
                plot_task_structure(task_ranges=trange, range_kwargs=range_kwargs, fig=fig)
        else:
            range_kwargs.setdefault('opacity', 0.25)
            for start, end in zip(*task_ranges):
                fig.add_shape(
                    type="rect",
                    x0=start, x1=end,
                    y0=0, y1=1,
                    xref="x", yref="paper",
                    fillcolor=range_kwargs.get('fillcolor', 'blue'),
                    opacity=range_kwargs['opacity'],
                    line_width=0,
                )

    # Add vertical lines
    if event_lines is not None:
        if not isinstance(event_lines[0], (int, float, np.int64, np.float64)):
            for eline, color in zip(event_lines, line_colors if line_colors else DEFAULT_COLORS):
                line_kwargs['line_color'] = color
                plot_task_structure(event_lines=list(eline), line_kwargs=line_kwargs, fig=fig)
        else:
            for line in event_lines:
                fig.add_shape(
                    type="line",
                    x0=line, x1=line,
                    y0=0, y1=1,
                    xref="x", yref="paper",
                    line=dict(
                        color=line_kwargs.get('line_color', 'black'),
                        width=line_kwargs.get('line_width', 2),
                    ),
                )

    # Add data points
    if data_points is not None:
        fig.add_trace(go.Scatter(
            x=data_points,
            y=[0.5] * len(data_points),
            mode='markers',
            marker=dict(size=10, color='red'),
            **plt_kwargs
        ))

    # Update layout
    fig.update_layout(
        yaxis=dict(visible=False),
        xaxis=dict(title="Time"),
        height=200,
        margin=dict(t=20, b=20, l=20, r=20),
    )

    return fig


@savefig
def plot_task_events(events, fig=None, **plt_kwargs):
    """Plot task events.

    Parameters
    ----------
    events : array or dict or list
        If array, indicates the times to plot event markers.
        If dict, should have the event markers as a 'times' key, plus any additional plot arguments.
        If list, can be a list of array or of dictionaries.
    fig : go.Figure, optional
        Plotly figure object to add elements to.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Create a new figure if one is not provided
    if fig is None:
        fig = go.Figure()

    events = listify(events)
    for event in events:
        if isinstance(event, (list, np.ndarray)):
            fig.add_trace(go.Scatter(
                x=event,
                y=[0.5] * len(event),
                mode='markers',
                marker=dict(size=10, color='blue'),
                **plt_kwargs
            ))
        elif isinstance(event, dict):
            times = event.pop('times')
            fig.add_trace(go.Scatter(
                x=times,
                y=[0.5] * len(times),
                mode='markers',
                marker=event.get('marker', dict(size=10, color='blue')),
                **event,
                **plt_kwargs
            ))

    # Update layout
    fig.update_layout(
        yaxis=dict(visible=False),
        xaxis=dict(title="Time"),
        height=200,
        margin=dict(t=20, b=20, l=20, r=20),
    )

    return fig
