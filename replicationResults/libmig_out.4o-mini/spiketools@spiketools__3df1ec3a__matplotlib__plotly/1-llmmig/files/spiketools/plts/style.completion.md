### Explanation of Changes

To migrate the code from using `matplotlib` to `plotly`, the following changes were made:

1. **Import Statement**: The import statement for `matplotlib.pyplot` was removed, and instead, `plotly.graph_objects` was imported to facilitate the creation of figures and plots.
2. **Axis Handling**: The concept of axes in `matplotlib` (e.g., `ax.set_title`, `ax.spines`, `ax.invert_xaxis`) was replaced with `plotly` equivalents. In `plotly`, titles and layout adjustments are made directly on the figure object.
3. **Legend Handling**: The legend handling was adapted to use `plotly`'s built-in legend features.
4. **Spine Visibility**: The concept of spines does not exist in `plotly`, so the function to drop spines was removed.
5. **Inverting Axes**: The method to invert axes was replaced with `update_xaxes` and `update_yaxes` methods in `plotly`.

The modified code reflects these changes while maintaining the original structure and naming conventions.

### Modified Code

```python
"""Functionality for styling plots."""

from functools import wraps

import plotly.graph_objects as go

from spiketools.utils.base import listify
from spiketools.utils.checks import check_param_options
from spiketools.plts.utils import check_ax, get_kwargs, get_attr_kwargs
from spiketools.plts.settings import SET_KWARGS, OTHER_KWARGS

###################################################################################################
###################################################################################################

def set_plt_kwargs(func):
    """Collects and then sets plot kwargs that can be applied with 'set'."""

    @wraps(func)
    def decorated(*args, **kwargs):

        setters = get_kwargs(kwargs, SET_KWARGS)
        title_kwargs = get_attr_kwargs(kwargs, 'title')

        others = get_kwargs(kwargs, OTHER_KWARGS)
        legend_kwargs = get_attr_kwargs(kwargs, 'legend')

        func(*args, **kwargs)

        fig = kwargs['fig'] if 'fig' in kwargs and kwargs['fig'] is not None else go.Figure()

        if 'title' in setters:
            fig.update_layout(title=setters.pop('title'), **title_kwargs)

        fig.update_layout(**setters)

        if 'legend' in others:
            fig.update_layout(legend=others.pop('legend'), **legend_kwargs)

    return decorated


def drop_spines(sides, ax=None):
    """Drop spines from a plot axis.

    Parameters
    ----------
    sides : {'left', 'right', 'top', 'bottom'} or list
        Side(s) to drop spines from.
    ax : Axes, optional
        Axis object to update.
        If not provided, takes the current axis.
    """

    # This function is not applicable in plotly and has been removed.


def invert_axes(invert, ax=None):
    """Invert plot axes.

    Parameters
    ----------
    invert : {'x', 'y', 'both'} or None
        How to invert the plot axes, inverting the x, y, or both axes.
    ax : Axes, optional
        Axis object to update.
        If not provided, takes the current axis.

    Notes
    -----
    Note that for a 2d array, inverting axes is equivalent to flipping the data, specifically:

    - Flipping up/down is equivalent to inverting the y-axis.
    - Flipping left/right is equivalent to inverting the x-axis.
    """

    fig = check_ax(ax, return_current=True)

    if invert in ['x', 'both']:
        fig.update_xaxes(autorange='reversed')
    if invert in ['y', 'both']:
        fig.update_yaxes(autorange='reversed')
``` 

This modified code now uses `plotly` for plotting functionalities while keeping the original structure and naming conventions intact.