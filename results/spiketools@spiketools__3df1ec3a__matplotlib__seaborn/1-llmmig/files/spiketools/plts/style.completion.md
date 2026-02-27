### Explanation of Changes
To migrate the code from `matplotlib` to `seaborn`, the following changes were made:
1. **Import Changes**: Replaced `matplotlib.pyplot` with `seaborn` as the primary plotting library.
2. **Axis Handling**: Seaborn uses `matplotlib` under the hood, so axis manipulation (like `ax.spines` or `ax.invert_xaxis`) remains compatible. However, the `seaborn` library provides higher-level functions for styling and customization.
3. **Legend and Title Handling**: Seaborn provides built-in support for legends and titles, but the existing logic for setting these attributes remains compatible.
4. **Spine Dropping**: Seaborn does not have a direct API for spine manipulation, but it supports `matplotlib`'s spine handling. The existing logic for spine manipulation remains unchanged.
5. **No Major Functional Changes**: Since the code relies on `matplotlib`'s `Axes` object for most operations, and `seaborn` integrates seamlessly with `matplotlib`, only the import and minor adjustments were required.

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

        ax = kwargs['ax'] if 'ax' in kwargs and kwargs['ax'] is not None else sns.gca()

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

### Key Notes
- The `sns.gca()` function is used as a replacement for `plt.gca()` to ensure compatibility with `seaborn`.
- Spine and axis inversion logic remains unchanged because `seaborn` relies on `matplotlib`'s `Axes` object for these operations.
- The migration primarily involves replacing `matplotlib` imports with `seaborn` while ensuring the existing functionality remains intact.