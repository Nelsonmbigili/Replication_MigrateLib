### Explanation of Changes

To migrate the provided code from using `matplotlib` to `altair`, several key changes were made:

1. **Import Statements**: The import statements were updated to include `altair` and remove `matplotlib` related imports.
2. **Plotting Functions**: The plotting logic was changed to use `altair`'s syntax for creating visualizations. This includes using `Chart`, `mark_area`, and `mark_rule` for shaded areas and vertical lines, respectively.
3. **Data Handling**: The data structure used in `altair` is different from `matplotlib`. Instead of directly plotting on axes, we create a `Chart` object and specify the data and encoding.
4. **Event Plotting**: The `eventplot` functionality was replaced with `mark_point` in `altair`, which allows for plotting points on the chart.

The overall structure of the functions remains the same, but the implementation details reflect the differences between the two libraries.

### Modified Code

```python
"""Plots for tasks and task structure related visualizations."""

import numpy as np
import altair as alt
import pandas as pd

from spiketools.utils.base import listify
from spiketools.plts.utils import check_ax, savefig
from spiketools.plts.style import set_plt_kwargs
from spiketools.plts.settings import DEFAULT_COLORS

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_task_structure(task_ranges=None, event_lines=None, data_points=None,
                        range_colors=None, line_colors=None, range_kwargs=None, line_kwargs=None,
                        ax=None, **plt_kwargs):
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
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Prepare data for Altair
    data = pd.DataFrame()

    if task_ranges is not None:
        if not isinstance(task_ranges[0][0], (int, float, np.int64, np.float64)):
            for trange, color in zip(task_ranges, range_colors if range_colors else DEFAULT_COLORS):
                range_kwargs['color'] = color
                plot_task_structure(task_ranges=trange, range_kwargs=range_kwargs, ax=ax)
        else:
            range_kwargs.setdefault('alpha', 0.25)
            shade_ranges = [[st, en] for st, en in zip(*task_ranges)]
            data = pd.DataFrame(shade_ranges, columns=['start', 'end'])
            chart = alt.Chart(data).mark_area(opacity=range_kwargs.get('alpha', 0.25), color=range_kwargs.get('color', 'lightgray')).encode(
                x='start:Q',
                x2='end:Q'
            )
            chart.display()

    if event_lines is not None:
        if not isinstance(event_lines[0], (int, float, np.int64, np.float64)):
            for eline, color in zip(event_lines, line_colors if line_colors else DEFAULT_COLORS):
                line_kwargs['color'] = color
                plot_task_structure(event_lines=list(eline), line_kwargs=line_kwargs, ax=ax)
        else:
            data = pd.DataFrame(event_lines, columns=['event'])
            chart = alt.Chart(data).mark_rule(color=line_kwargs.get('color', 'black')).encode(
                x='event:Q'
            )
            chart.display()

    if data_points is not None:
        data = pd.DataFrame(data_points, columns=['data_point'])
        chart = alt.Chart(data).mark_point().encode(
            x='data_point:Q'
        )
        chart.display()

    # Note: Altair does not have a direct equivalent for set_yticks, as it handles axes differently.

@savefig
@set_plt_kwargs
def plot_task_events(events, ax=None, **plt_kwargs):
    """Plot task events.

    Parameters
    ----------
    events : array or dict or list
        If array, indicates the times to plot event markers.
        If dict, should have the event markers as a 'times' key, plus any additional plot arguments.
        If list, can be a list of array or of dictionaries.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Prepare data for Altair
    data = pd.DataFrame()

    events = listify(events)
    for event in events:
        if isinstance(event, (list, np.ndarray)):
            data = pd.DataFrame(event, columns=['event'])
            chart = alt.Chart(data).mark_point().encode(
                x='event:Q'
            )
            chart.display()
        elif isinstance(event, dict):
            data = pd.DataFrame(event.pop('times'), columns=['event'])
            chart = alt.Chart(data).mark_point().encode(
                x='event:Q'
            )
            chart.display()
```

This modified code now uses `altair` for plotting instead of `matplotlib`, while maintaining the original function signatures and overall structure.