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
