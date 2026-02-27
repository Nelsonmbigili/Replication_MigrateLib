import plotly.graph_objects as go
import pytest


@pytest.fixture(scope='module', autouse=True)
def clear_previous_plot():
    pass  # No equivalent function needed in Plotly
