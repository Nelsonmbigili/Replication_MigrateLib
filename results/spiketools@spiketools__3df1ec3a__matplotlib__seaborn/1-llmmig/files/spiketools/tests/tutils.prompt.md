The following Python code currently uses the library "matplotlib" version 3.10.1.
Migrate this code to use the library "seaborn" version 0.13.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "matplotlib" to "seaborn".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "matplotlib" and "seaborn".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""Utilities for tests."""

from functools import wraps

import matplotlib.pyplot as plt

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