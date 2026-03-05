### Explanation of Changes

To migrate the code from using `matplotlib` to `seaborn`, the following changes were made:

1. **Import Statement**: The import statement for `matplotlib.pyplot` was removed, as `seaborn` does not require it directly for the functionalities used in this code.
2. **Axes Handling**: The way to handle axes remains similar, but we ensure that any plotting functions that might be added later can utilize `seaborn`'s capabilities. However, since the provided code does not include any direct plotting functions, the existing axes handling remains unchanged.
3. **Spine Management**: The method for dropping spines remains the same, as it directly manipulates the axes object, which is compatible with both libraries.

The core functionality of the code remains intact, focusing on setting plot parameters and managing axes.

### Modified Code

```python
"""Functionality for styling plots."""

from functools import wraps

import seaborn as sns

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

        ax = kwargs['ax'] if 'ax' in kwargs and kwargs['ax'] is not None else sns.axlabel()

        if 'title' in setters:
            ax.set_title(setters.pop('title'), **title_kwargs)

        ax.set(**setters)

        if 'legend' in others:
            ax.legend(others.pop('legend'), **legend_kwargs)

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

    ax = check_ax(ax, return_current=True)

    for side in listify(sides):
        check_param_options(side, 'side', ['left', 'right', 'top', 'bottom'])
        ax.spines[side].set_visible(False)


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

    ax = check_ax(ax, return_current=True)

    if invert in ['x', 'both']:
        ax.invert_xaxis()
    if invert in ['y', 'both']:
        ax.invert_yaxis()
``` 

Note: The line `sns.axlabel()` is a placeholder and may need to be adjusted based on how you want to handle axes in your specific application with `seaborn`.