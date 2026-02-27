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
