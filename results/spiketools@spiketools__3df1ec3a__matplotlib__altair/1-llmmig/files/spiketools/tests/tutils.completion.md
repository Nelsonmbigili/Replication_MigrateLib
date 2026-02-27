### Explanation of Changes:
To migrate the code from `matplotlib` to `altair`, the following changes were made:
1. Removed the import of `matplotlib.pyplot` since it is no longer needed.
2. Replaced the `plt.close('all')` calls with equivalent logic for `altair`. Since `altair` does not maintain a global state for figures or axes like `matplotlib`, there is no need to explicitly close plots.
3. Replaced the checks for `plt.gca()` (current axis) and `plt.gcf()` (current figure) with equivalent logic for `altair`. In `altair`, charts are created as objects, so the checks were updated to ensure that a valid `altair.Chart` object is created and contains data.

### Modified Code:
```python
"""Utilities for tests."""

from functools import wraps
import altair as alt

###################################################################################################
###################################################################################################

def plot_test(func):
    """Decorator for simple testing of plotting functions.

    Notes
    -----
    This decorator ensures that the test function creates a valid Altair chart with data.
    It therefore performs a minimal test - asserting the chart exists, with no accuracy checking.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # Run the test function
        chart = func(*args, **kwargs)

        # Check that the returned object is a valid Altair chart
        assert isinstance(chart, alt.Chart), "The function did not return an Altair Chart object."

        # Check that the chart contains data
        assert chart.data is not None, "The chart does not contain any data."

    return wrapper


def fig_test(func):
    """Decorator for simple testing of functions that create a figure.

    Notes
    -----
    This decorator ensures that the test function creates a valid Altair chart with data.
    It therefore performs a minimal test - asserting the chart exists, with no accuracy checking.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        # Run the test function
        chart = func(*args, **kwargs)

        # Check that the returned object is a valid Altair chart
        assert isinstance(chart, alt.Chart), "The function did not return an Altair Chart object."

        # Check that the chart contains data
        assert chart.data is not None, "The chart does not contain any data."

    return wrapper
```

### Key Notes:
- In `altair`, charts are created as objects, and there is no global state for figures or axes. This eliminates the need for `plt.close('all')` or accessing global objects like `plt.gca()` or `plt.gcf()`.
- The `plot_test` and `fig_test` decorators now ensure that the test functions return a valid `altair.Chart` object and that the chart contains data.
- The logic for testing remains minimal, as per the original code, focusing only on the existence of a chart and its data.