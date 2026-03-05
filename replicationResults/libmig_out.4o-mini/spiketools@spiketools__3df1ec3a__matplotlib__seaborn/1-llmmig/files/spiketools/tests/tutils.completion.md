### Explanation of Changes
To migrate the code from using the `matplotlib` library to the `seaborn` library, I made the following changes:

1. **Import Statement**: Changed the import from `matplotlib.pyplot` to `seaborn`. Since `seaborn` is built on top of `matplotlib`, it still allows for the use of `matplotlib` functions, but we will primarily use `seaborn` for plotting.
2. **Plotting Functions**: The original code does not contain specific plotting functions, but it relies on `plt.gca()` and `plt.gcf()` to get the current axis and figure, respectively. These functions are still valid in the context of `seaborn`, as it uses `matplotlib` under the hood.

The overall structure of the decorators remains unchanged, as they are designed to test plotting functions and figures, which can still be applicable when using `seaborn`.

### Modified Code
```python
"""Utilities for tests."""

from functools import wraps

import seaborn as sns

###################################################################################################
###################################################################################################

def plot_test(func):
    """Decorator for simple testing of plotting functions.

    Notes
    -----
    This decorator closes all plots prior to the test.
    After running the test function, it checks an axis was created with data.
    It therefore performs a minimal test - asserting the plots exists, with no accuracy checking.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        plt.close('all')

        func(*args, **kwargs)

        ax = plt.gca()
        assert ax.has_data()

    return wrapper


def fig_test(func):
    """Decorator for simple testing of function that create a figure.

    Notes
    -----
    This decorator closes all plots prior to the test.
    After running the test function, it checks a figure was created, including an axis.
    It therefore performs a minimal test - asserting the figure exists, with no accuracy checking.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        plt.close('all')

        func(*args, **kwargs)

        fig = plt.gcf()
        assert fig.axes

    return wrapper
```

Note: The `plt` calls remain unchanged because `seaborn` does not replace `matplotlib`'s plotting functions; it enhances them. If you want to fully transition to `seaborn`, you would typically replace specific plotting calls in the functions being tested, but those details were not provided in the original code.