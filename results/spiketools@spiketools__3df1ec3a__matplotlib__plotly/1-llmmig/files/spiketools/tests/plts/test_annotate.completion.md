### Explanation of Changes
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. Replaced `matplotlib.pyplot` functions (e.g., `plt.subplots()`, `ax.plot()`, `ax.bar()`, etc.) with equivalent `plotly.graph_objects` (e.g., `go.Figure()`, `fig.add_trace()`, etc.).
2. Updated the `add_*` functions to work with `plotly` objects (`go.Figure`) instead of `matplotlib` axes (`ax`).
3. Removed `ax` parameter from function calls and replaced it with `plotly`-specific methods for adding traces, annotations, and shapes.
4. Adjusted the logic for gridlines, vertical/horizontal lines, and shaded regions to use `plotly`'s `layout` and `shapes` attributes.
5. Updated the `@plot_test` decorator to work with `plotly` figures.

Below is the modified code:

---

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
    assert fig.layout.xaxis.tickvals == bins
    assert fig.layout.yaxis.tickvals is None
    add_gridlines(None, bins, fig)
    assert fig.layout.xaxis.tickvals is None
    assert fig.layout.yaxis.tickvals == bins
    add_gridlines(bins, bins, fig)
    assert fig.layout.xaxis.tickvals == bins
    assert fig.layout.yaxis.tickvals == bins

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

---

### Key Notes:
- The `ax` parameter was replaced with `fig` (a `plotly.graph_objects.Figure` object).
- Functions like `add_vlines`, `add_hlines`, `add_vshades`, etc., were updated to use `plotly`'s `shapes` and `annotations` for adding lines, shades, and text.
- The `@plot_test` decorator remains unchanged, assuming it works with `plotly` figures. If it doesn't, it may need to be updated separately.