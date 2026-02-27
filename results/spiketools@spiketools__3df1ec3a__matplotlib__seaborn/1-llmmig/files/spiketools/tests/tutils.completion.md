### Explanation of Changes
To migrate the code from `matplotlib` to `seaborn`, the following changes were made:
1. **Import Replacement**: Replaced the `matplotlib.pyplot` import (`import matplotlib.pyplot as plt`) with `seaborn` (`import seaborn as sns`).
2. **Plot Management**: Seaborn does not have direct equivalents for `plt.close('all')`, `plt.gca()`, or `plt.gcf()` because it is built on top of `matplotlib`. However, Seaborn integrates with `matplotlib` for figure and axis management. To maintain compatibility, I retained the use of `matplotlib`'s figure and axis management functions (`plt.close`, `plt.gca`, and `plt.gcf`) since Seaborn relies on them internally.
3. **No Changes to Logic**: The logic of the decorators remains unchanged because the functionality (closing plots, checking for axes, and figures) is still valid when using Seaborn.

### Modified Code
```python
"""Utilities for tests."""

from functools import wraps

import seaborn as sns
import matplotlib.pyplot as plt  # Retained for figure and axis management

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

        plt.close('all')  # Close all plots (still valid with Seaborn)

        func(*args, **kwargs)

        ax = plt.gca()  # Get the current axis (Seaborn uses matplotlib axes)
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

        plt.close('all')  # Close all plots (still valid with Seaborn)

        func(*args, **kwargs)

        fig = plt.gcf()  # Get the current figure (Seaborn uses matplotlib figures)
        assert fig.axes

    return wrapper
```

### Key Notes
- The `matplotlib.pyplot` import is retained alongside `seaborn` because Seaborn relies on `matplotlib` for figure and axis management.
- The logic of the decorators remains unchanged, as the functionality of `plt.close`, `plt.gca`, and `plt.gcf` is still valid when using Seaborn.
- No additional Seaborn-specific functionality was introduced, as the original code does not directly create plots or use specific plotting functions.