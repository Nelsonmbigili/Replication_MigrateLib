import altair as alt
import pytest


@pytest.fixture(scope='module', autouse=True)
def clear_previous_plot():
    pass  # No need to clear previous plots in Altair
