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

        fig = func(*args, **kwargs)

        if 'title' in setters:
            fig.update_layout(title=dict(text=setters.pop('title'), **title_kwargs))

        fig.update_layout(**setters)

        if 'legend' in others:
            fig.update_layout(legend=dict(title=others.pop('legend'), **legend_kwargs))

        return fig

    return decorated


def drop_spines(sides, ax=None):
    """Drop spines from a plot axis.

    Parameters
    ----------
    sides : {'left', 'right', 'top', 'bottom'} or list
        Side(s) to drop spines from.
    ax : Figure, optional
        Figure object to update.
        If not provided, assumes a new figure is being created.
    """

    ax = check_ax(ax, return_current=True)

    updates = {}
    for side in listify(sides):
        check_param_options(side, 'side', ['left', 'right', 'top', 'bottom'])
        if side == 'left':
            updates['yaxis.showline'] = False
        elif side == 'right':
            updates['yaxis.mirror'] = False
        elif side == 'top':
            updates['xaxis.mirror'] = False
        elif side == 'bottom':
            updates['xaxis.showline'] = False

    ax.update_layout(**updates)


def invert_axes(invert, ax=None):
    """Invert plot axes.

    Parameters
    ----------
    invert : {'x', 'y', 'both'} or None
        How to invert the plot axes, inverting the x, y, or both axes.
    ax : Figure, optional
        Figure object to update.
        If not provided, assumes a new figure is being created.

    Notes
    -----
    Note that for a 2d array, inverting axes is equivalent to flipping the data, specifically:

    - Flipping up/down is equivalent to inverting the y-axis.
    - Flipping left/right is equivalent to inverting the x-axis.
    """

    ax = check_ax(ax, return_current=True)

    if invert in ['x', 'both']:
        ax.update_layout(xaxis_autorange='reversed')
    if invert in ['y', 'both']:
        ax.update_layout(yaxis_autorange='reversed')
