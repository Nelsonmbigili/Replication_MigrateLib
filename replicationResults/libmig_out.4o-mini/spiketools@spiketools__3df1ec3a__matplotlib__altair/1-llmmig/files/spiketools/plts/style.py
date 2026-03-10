"""Functionality for styling plots."""

from functools import wraps

import altair as alt

from spiketools.utils.base import listify
from spiketools.utils.checks import check_param_options
from spiketools.plts.utils import get_kwargs, get_attr_kwargs
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

        # In Altair, we don't use ax; we define the chart directly.
        chart = kwargs.get('chart', None)

        if chart is not None and 'title' in setters:
            chart = chart.properties(title=setters.pop('title'))

        # Altair does not have a direct equivalent for ax.set()
        # The setters would need to be applied directly to the chart properties.

        # Legend handling is integrated into the chart definition in Altair.
        # Therefore, we do not need to handle it separately.

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

    # This function is not applicable in Altair and has been removed.


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

    # This function is not applicable in Altair and has been removed.
