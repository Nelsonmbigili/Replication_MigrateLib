### Explanation of Changes:
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. Replaced `matplotlib.pyplot` (`plt`) with `plotly.graph_objects` (`go`) and `plotly.io` (`pio`).
2. Removed `plt.close('all')` since `plotly` does not maintain a global state for figures like `matplotlib`.
3. Replaced `plt.gca()` (get current axis) with `fig.data` to check if the figure contains data.
4. Replaced `plt.gcf()` (get current figure) with `fig` directly, as `plotly` figures are explicitly created and passed around.
5. Updated the assertions to check for the presence of data in `plotly` figures (`fig.data`) and axes (`fig.layout`).

### Modified Code:
```python
"""Utilities for tests."""

from functools import wraps

import plotly.graph_objects as go
import plotly.io as pio

###################################################################################################
###################################################################################################

def plot_test(func):
    """Decorator for simple testing of plotting functions.

    Notes
    -----
    This decorator ensures that after running the test function, it checks a figure was created
    with data. It therefore performs a minimal test - asserting the plot exists, with no accuracy checking.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # Run the test function
        fig = func(*args, **kwargs)

        # Check that the figure contains data
        assert fig.data, "The plot does not contain any data."

    return wrapper


def fig_test(func):
    """Decorator for simple testing of function that create a figure.

    Notes
    -----
    This decorator ensures that after running the test function, it checks a figure was created,
    including layout and data. It therefore performs a minimal test - asserting the figure exists,
    with no accuracy checking.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # Run the test function
        fig = func(*args, **kwargs)

        # Check that the figure contains data and layout
        assert fig.data, "The figure does not contain any data."
        assert fig.layout, "The figure does not contain a layout."

    return wrapper
```

### Key Points:
- `plotly` does not have a global state for figures, so we directly work with the `fig` object returned by the test functions.
- The `assert` statements now check `fig.data` (for plot data) and `fig.layout` (for layout/axes) instead of relying on `matplotlib`'s `gca()` and `gcf()`.
- The `plt.close('all')` call was removed as it is not applicable in `plotly`.