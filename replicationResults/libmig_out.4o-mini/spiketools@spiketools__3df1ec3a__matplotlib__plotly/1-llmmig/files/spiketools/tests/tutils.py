"""Utilities for tests."""

from functools import wraps
import plotly.graph_objects as go

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

        # No need to close plots in Plotly

        func(*args, **kwargs)

        fig = go.Figure()  # Create a new figure to check for traces
        assert len(fig.data) > 0  # Check if there is at least one trace

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

        # No need to close plots in Plotly

        func(*args, **kwargs)

        fig = go.Figure()  # Create a new figure to check for traces
        assert len(fig.data) > 0  # Check if there is at least one trace

    return wrapper
