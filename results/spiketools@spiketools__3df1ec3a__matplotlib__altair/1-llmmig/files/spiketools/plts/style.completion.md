### Explanation of Changes
The original code uses `matplotlib` for plotting and styling, which involves directly manipulating `Axes` objects. To migrate to `altair`, which is a declarative visualization library, the following changes were made:
1. **Removed `matplotlib` imports**: All references to `matplotlib.pyplot` and `Axes` objects were removed.
2. **Replaced `set_plt_kwargs`**: Since `altair` does not use `Axes` objects or `set` methods, the function was rewritten to apply plot-level configurations (like titles and legends) using `altair.Chart` properties.
3. **Replaced `drop_spines`**: `altair` does not use spines in the same way as `matplotlib`. Instead, axis visibility is controlled using `alt.Axis` properties. The function was rewritten to hide specific axes.
4. **Replaced `invert_axes`**: In `altair`, axis inversion is achieved by setting the `scale` property of the axis to `reverse=True`. The function was updated accordingly.
5. **Preserved Function Signatures**: The function names, parameters, and overall structure were kept the same to ensure compatibility with the rest of the application.

### Modified Code
```python
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

        chart = func(*args, **kwargs)

        # Apply title if specified
        if 'title' in setters:
            chart = chart.properties(
                title=alt.TitleParams(setters.pop('title'), **title_kwargs)
            )

        # Apply legend settings if specified
        if 'legend' in others:
            chart = chart.configure_legend(**legend_kwargs)

        return chart

    return decorated


def drop_spines(sides, chart=None):
    """Drop spines from a plot axis.

    Parameters
    ----------
    sides : {'left', 'right', 'top', 'bottom'} or list
        Side(s) to drop spines from.
    chart : alt.Chart, optional
        Chart object to update.
        If not provided, assumes a chart is being created in the calling function.
    """

    for side in listify(sides):
        check_param_options(side, 'side', ['left', 'right', 'top', 'bottom'])

    # Configure axis visibility based on sides
    axis_config = {}
    if 'left' in sides:
        axis_config['y'] = alt.Axis(domain=False, ticks=False, labels=False)
    if 'right' in sides:
        axis_config['y'] = alt.Axis(domain=False, ticks=False, labels=False)
    if 'top' in sides:
        axis_config['x'] = alt.Axis(domain=False, ticks=False, labels=False)
    if 'bottom' in sides:
        axis_config['x'] = alt.Axis(domain=False, ticks=False, labels=False)

    return chart.configure_axis(**axis_config)


def invert_axes(invert, chart=None):
    """Invert plot axes.

    Parameters
    ----------
    invert : {'x', 'y', 'both'} or None
        How to invert the plot axes, inverting the x, y, or both axes.
    chart : alt.Chart, optional
        Chart object to update.
        If not provided, assumes a chart is being created in the calling function.

    Notes
    -----
    Note that for a 2d array, inverting axes is equivalent to flipping the data, specifically:

    - Flipping up/down is equivalent to inverting the y-axis.
    - Flipping left/right is equivalent to inverting the x-axis.
    """

    if invert in ['x', 'both']:
        chart = chart.encode(x=alt.X(chart.encoding.x.shorthand, scale=alt.Scale(reverse=True)))
    if invert in ['y', 'both']:
        chart = chart.encode(y=alt.Y(chart.encoding.y.shorthand, scale=alt.Scale(reverse=True)))

    return chart
```

### Key Notes
- The `set_plt_kwargs` function now applies configurations like titles and legends using `altair.Chart` properties and configuration methods.
- The `drop_spines` function was adapted to hide axes by configuring `alt.Axis` properties.
- The `invert_axes` function modifies the axis scales to reverse the direction using `alt.Scale(reverse=True)`.
- The `chart` object is passed and returned in each function to allow chaining of `altair` configurations.