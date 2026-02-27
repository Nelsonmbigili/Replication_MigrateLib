"""Plots for tasks and task structure related visualizations."""

import numpy as np
import pandas as pd
import altair as alt

from spiketools.utils.base import listify
from spiketools.plts.utils import savefig
from spiketools.plts.style import set_plt_kwargs
from spiketools.plts.settings import DEFAULT_COLORS

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_task_structure(task_ranges=None, event_lines=None, data_points=None,
                        range_colors=None, line_colors=None, range_kwargs=None, line_kwargs=None,
                        **plt_kwargs):
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
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Prepare data for task ranges
    if task_ranges is not None:
        if not isinstance(task_ranges[0][0], (int, float, np.int64, np.float64)):
            task_ranges = [item for sublist in task_ranges for item in sublist]
        task_ranges_df = pd.DataFrame(task_ranges, columns=['start', 'end'])
        task_ranges_df['color'] = range_colors if range_colors else DEFAULT_COLORS[:len(task_ranges_df)]

    # Prepare data for event lines
    if event_lines is not None:
        if not isinstance(event_lines[0], (int, float, np.int64, np.float64)):
            event_lines = [item for sublist in event_lines for item in sublist]
        event_lines_df = pd.DataFrame({'time': event_lines})
        event_lines_df['color'] = line_colors if line_colors else DEFAULT_COLORS[:len(event_lines_df)]

    # Prepare data for data points
    if data_points is not None:
        data_points_df = pd.DataFrame({'time': data_points})

    # Create Altair chart
    base = alt.Chart().properties(width=plt_kwargs.get('figsize', (800, 100))[0],
                                  height=plt_kwargs.get('figsize', (800, 100))[1])

    # Add task ranges as shaded areas
    if task_ranges is not None:
        range_chart = base.mark_rect(opacity=range_kwargs.get('alpha', 0.25)).encode(
            x='start:Q',
            x2='end:Q',
            color=alt.Color('color:N', scale=None)
        ).transform_calculate(color='datum.color')
    else:
        range_chart = None

    # Add event lines
    if event_lines is not None:
        line_chart = base.mark_rule(**line_kwargs).encode(
            x='time:Q',
            color=alt.Color('color:N', scale=None)
        ).transform_calculate(color='datum.color')
    else:
        line_chart = None

    # Add data points
    if data_points is not None:
        point_chart = base.mark_point().encode(
            x='time:Q'
        )
    else:
        point_chart = None

    # Combine charts
    charts = [chart for chart in [range_chart, line_chart, point_chart] if chart is not None]
    final_chart = alt.layer(*charts) if charts else alt.Chart()

    return final_chart


@savefig
@set_plt_kwargs
def plot_task_events(events, **plt_kwargs):
    """Plot task events.

    Parameters
    ----------
    events : array or dict or list
        If array, indicates the times to plot event markers.
        If dict, should have the event markers as a 'times' key, plus any additional plot arguments.
        If list, can be a list of array or of dictionaries.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Prepare data for events
    events = listify(events)
    event_data = []
    for event in events:
        if isinstance(event, (list, np.ndarray)):
            event_data.extend(event)
        elif isinstance(event, dict):
            times = event.pop('times')
            event_data.extend(times)

    event_df = pd.DataFrame({'time': event_data})

    # Create Altair chart
    chart = alt.Chart(event_df).mark_point().encode(
        x='time:Q'
    ).properties(width=plt_kwargs.get('figsize', (800, 100))[0],
                 height=plt_kwargs.get('figsize', (800, 100))[1])

    return chart
