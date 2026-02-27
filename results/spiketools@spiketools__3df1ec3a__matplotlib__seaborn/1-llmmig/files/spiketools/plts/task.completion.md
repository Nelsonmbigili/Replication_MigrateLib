### Explanation of Changes
To migrate the code from `matplotlib` to `seaborn`, the following changes were made:
1. **Shaded Ranges (`add_vshades`)**: Replaced the custom `add_vshades` function with `seaborn`'s `sns.despine()` and `ax.fill_between()` for shading ranges.
2. **Vertical Lines (`add_vlines`)**: Replaced the custom `add_vlines` function with `seaborn`'s `ax.axvline()` for drawing vertical lines.
3. **Event Plot (`ax.eventplot`)**: Replaced `ax.eventplot` with `seaborn`'s `sns.scatterplot()` for plotting event markers.
4. **Styling**: Ensured that `seaborn`'s default styles are applied by using `sns.set_theme()`.

The rest of the code structure, including function signatures and logic, remains unchanged to ensure compatibility with the larger application.

---

### Modified Code
```python
"""Plots for tasks and task structure related visualizations."""

import numpy as np
import seaborn as sns

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

    sns.set_theme(style="whitegrid")
    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', (16, 2)))

    range_kwargs = {} if range_kwargs is None else range_kwargs
    line_kwargs = {} if line_kwargs is None else line_kwargs

    if task_ranges is not None:
        if not isinstance(task_ranges[0][0], (int, float, np.int64, np.float64)):
            for trange, color in zip(task_ranges, range_colors if range_colors else DEFAULT_COLORS):
                range_kwargs['color'] = color
                plot_task_structure(task_ranges=trange, range_kwargs=range_kwargs, ax=ax)
        else:
            range_kwargs.setdefault('alpha', 0.25)
            for start, end in zip(*task_ranges):
                ax.fill_between([start, end], 0, 1, transform=ax.get_xaxis_transform(), **range_kwargs)

    if event_lines is not None:
        if not isinstance(event_lines[0], (int, float, np.int64, np.float64)):
            for eline, color in zip(event_lines, line_colors if line_colors else DEFAULT_COLORS):
                line_kwargs['color'] = color
                plot_task_structure(event_lines=list(eline), line_kwargs=line_kwargs, ax=ax)
        else:
            for line in event_lines:
                ax.axvline(line, **line_kwargs)

    if data_points is not None:
        sns.scatterplot(x=data_points, y=[0] * len(data_points), ax=ax, **plt_kwargs)

    ax.set_yticks([])
    sns.despine(ax=ax, left=True)


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

    sns.set_theme(style="whitegrid")
    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', (16, 2)))

    events = listify(events)
    for event in events:
        if isinstance(event, (list, np.ndarray)):
            sns.scatterplot(x=event, y=[0] * len(event), ax=ax, **plt_kwargs)
        elif isinstance(event, dict):
            sns.scatterplot(x=event.pop('times'), y=[0] * len(event['times']), ax=ax, **event, **plt_kwargs)

    sns.despine(ax=ax, left=True)
```

---

### Key Notes
- The `sns.set_theme()` function is used to apply `seaborn`'s default styling.
- `ax.fill_between()` is used for shading ranges, replacing `add_vshades`.
- `ax.axvline()` is used for vertical lines, replacing `add_vlines`.
- `sns.scatterplot()` is used for event markers, replacing `ax.eventplot`.
- The `sns.despine()` function is used to remove unnecessary spines for cleaner plots.