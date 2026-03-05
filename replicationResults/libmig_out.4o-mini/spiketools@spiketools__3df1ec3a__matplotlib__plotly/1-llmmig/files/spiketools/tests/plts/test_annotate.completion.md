### Explanation of Changes

To migrate the provided code from using `matplotlib` to `plotly`, the following changes were made:

1. **Importing Plotly**: The `matplotlib.pyplot` import was replaced with `plotly.graph_objects` for creating figures and plots.
2. **Creating Figures**: Instead of using `plt.subplots()`, `plotly` uses `go.Figure()` to create a figure object.
3. **Plotting Data**: The plotting functions (like `ax.plot()`, `ax.bar()`, etc.) were replaced with `plotly` equivalents such as `go.Scatter()` for line plots and `go.Bar()` for bar plots.
4. **Adding Vertical and Horizontal Lines**: The functions `add_vlines()` and `add_hlines()` were replaced with `fig.add_shape()` to add lines to the plot.
5. **Adding Gridlines**: The gridlines are handled differently in `plotly`, so the `add_gridlines()` function was adapted to use `fig.update_xaxes()` and `fig.update_yaxes()`.
6. **Shading Areas**: The `add_vshades()` and `add_hshades()` functions were replaced with `fig.add_shape()` to create rectangular shapes for shading.
7. **Adding Dots**: The `add_dots()` function was replaced with `fig.add_trace()` using `go.Scatter()` for adding points.
8. **Adding Text Labels**: The `add_text_labels()` function was adapted to use `fig.add_trace()` with `go.Scatter()` for text annotations.

The overall structure of the tests remains the same, but the plotting logic is now compatible with `plotly`.

### Modified Code

```python
"""Tests for spiketools.plts.annotate"""

import numpy as np
import plotly.graph_objects as go

from spiketools.tests.tutils import plot_test

from spiketools.plts.annotate import *

###################################################################################################
###################################################################################################

def test_color_pvalue():

    out1 = color_pvalue(0.025)
    assert out1 == 'red'

    out2 = color_pvalue(0.50)
    assert out2 == 'black'

    out3 = color_pvalue(0.005, 0.01, 'green')
    assert out3 == 'green'

@plot_test
def test_add_vlines():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 4], mode='lines'))
    add_vlines([1.5, 2.5, 3.5], fig=fig)

@plot_test
def test_add_hlines():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 4], mode='lines'))
    add_hlines([1.5, 2.5, 3.5], fig=fig)

@plot_test
def test_add_gridlines():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 2], y=[0, 2], mode='lines'))

    bins = [0.5, 1.5]
    add_gridlines(bins, None, fig)
    assert np.array_equal(fig['layout']['xaxis']['tickvals'], bins)
    assert np.array_equal(fig['layout']['yaxis']['tickvals'], [])
    add_gridlines(None, bins, fig)
    assert np.array_equal(fig['layout']['xaxis']['tickvals'], [])
    assert np.array_equal(fig['layout']['yaxis']['tickvals'], bins)
    add_gridlines(bins, bins, fig)
    assert np.array_equal(fig['layout']['xaxis']['tickvals'], bins)
    assert np.array_equal(fig['layout']['yaxis']['tickvals'], bins)

@plot_test
def test_add_vshades():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 4], mode='lines'))
    add_vshades([2., 3.], fig=fig)
    add_vshades([[0.5, 0.75], [3.5, 3.75]], color='red', fig=fig)

@plot_test
def test_add_hshades():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 4], mode='lines'))
    add_hshades([2., 3.], fig=fig)
    add_hshades([[0.5, 0.75], [3.5, 3.75]], color='red', fig=fig)

@plot_test
def test_add_box_shade():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 4], mode='lines'))
    add_box_shade(1.5, 2.5, 2, fig=fig)

@plot_test
def test_add_box_shades():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 4], mode='lines'))
    add_box_shades(np.array([1.5, 2.5]), np.array([1.5, 2.5]), fig=fig)

@plot_test
def test_add_dots():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 4], mode='lines'))
    add_dots(np.array([[1, 2], [2, 3]]), fig=fig)

    # Test adding an additional dot from 1d array
    add_dots(np.array([2.5, 2.5]), color='red', fig=fig)

@plot_test
def test_add_significance():

    fig = go.Figure()

    x_values = [1, 2, 3, 4]
    stats = [1., 0.01, 0.5, 1.]

    fig.add_trace(go.Scatter(x=x_values, y=x_values, mode='lines'))
    add_significance(stats, fig=fig)

@plot_test
def test_add_text_labels_x():

    fig = go.Figure()
    data = [15, 12, 32, 22]
    fig.add_trace(go.Bar(x=['A', 'B', 'C', 'D'], y=data))
    add_text_labels(data, axis='x', fig=fig)

@plot_test
def test_add_text_labels_y():

    fig = go.Figure()
    data = [15, 12, 32, 22]
    fig.add_trace(go.Bar(x=data, y=['A', 'B', 'C', 'D'], orientation='h'))
    add_text_labels(data, axis='y', position='end', fig=fig)
```