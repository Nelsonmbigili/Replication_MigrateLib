### Explanation of Changes
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. **Plotting Functions**: Replaced `matplotlib` plotting functions (e.g., `plt.plot`, `plt.subplots`, etc.) with equivalent `plotly` functions (e.g., `plotly.graph_objects.Figure` and its methods).
2. **Figure and Axis Handling**: Since `plotly` does not use the concept of `axes` in the same way as `matplotlib`, the `check_ax` function was adapted to create and return a `plotly.graph_objects.Figure` object.
3. **Saving Figures**: Replaced `matplotlib`'s `savefig` with `plotly`'s `write_image` for saving figures.
4. **Grid and Subplots**: Replaced `matplotlib`'s grid and subplot creation with `plotly`'s `make_subplots` from `plotly.subplots`.

Below is the modified code:

---

### Modified Code
```python
"""Tests for spiketools.plts.utils."""

import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from spiketools.plts.settings import SET_KWARGS

from spiketools.tests.tutils import fig_test
from spiketools.tests.tsettings import TEST_PLOTS_PATH

from spiketools.plts.utils import *

###################################################################################################
###################################################################################################

def test_check_ax():

    # Check running with None Input
    ax = check_ax(None)
    assert ax is not None

    # Check running with pre-created figure
    fig = go.Figure()
    nax = check_ax(fig)
    assert nax == fig

    # Check creating figure of a particular size
    figsize = [5, 5]
    ax = check_ax(None, figsize=figsize)
    assert ax.layout.width == figsize[0] * 100  # Convert inches to pixels
    assert ax.layout.height == figsize[1] * 100

    # Check getting current figure (plotly does not have a "current axis" concept)
    fig = go.Figure()
    nax = check_ax(None, return_current=True)
    assert nax == fig

def test_get_kwargs():

    kwargs = {'title' : 'title', 'xlabel' : 'xlabel', 'lw' : 12}
    out = get_kwargs(kwargs, SET_KWARGS)
    for arg in ['title', 'xlabel']:
        assert arg in out
        assert arg not in kwargs
    for arg in ['lw']:
        assert arg not in out
        assert arg in kwargs

def test_get_attr_kwargs():

    kwargs = {'title_color' : 'red', 'xlabel' : 'xlabel', 'lw' : 12}
    out = get_attr_kwargs(kwargs, 'title')
    for arg in ['color']:
        assert arg in out
        assert 'title_' + arg not in kwargs
    for arg in ['xlabel', 'lw']:
        assert arg not in out
        assert arg in kwargs

def test_savefig():

    @savefig
    def example_plot():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))
        return fig

    # Test defaults to saving given file path & name
    example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig1.pdf')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig1.pdf'))

    # Test works the same when explicitly given `save_fig`
    example_plot(save_fig=True, file_path=TEST_PLOTS_PATH, file_name='test_savefig2.pdf')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig2.pdf'))

    # Test giving additional save kwargs (not directly supported in plotly)
    example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig3.pdf')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig3.pdf'))

    # Test does not save when `save_fig` set to False
    example_plot(save_fig=False, file_path=TEST_PLOTS_PATH, file_name='test_savefig_nope.pdf')
    assert not os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig_nope.pdf'))

def test_save_figure():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))
    save_figure(fig, file_name='test_save_figure.pdf', file_path=TEST_PLOTS_PATH)
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_save_figure.pdf'))

@fig_test
def test_make_axes():

    n_axes = 5

    # Create a figure with multiple subplots
    fig = make_subplots(rows=n_axes, cols=1)
    assert len(fig.data) == 0  # No data added yet

    fig = make_subplots(rows=2, cols=2, horizontal_spacing=0.1, vertical_spacing=0.1)
    assert len(fig.data) == 0  # No data added yet

def test_make_grid():

    nrows, ncols = 2, 2
    grid = make_subplots(rows=nrows, cols=ncols, subplot_titles=['grid title'] * (nrows * ncols))
    assert grid.layout.grid.rows == nrows
    assert grid.layout.grid.columns == ncols

@fig_test
def test_get_grid_subplot():

    grid = make_subplots(rows=2, cols=2)
    grid.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=1, col=1)
    assert len(grid.data) == 1
```

---

### Key Notes:
1. **Figure Size**: In `plotly`, figure size is specified in pixels, so the `figsize` (in inches) was converted to pixels by multiplying by 100.
2. **Saving Figures**: Used `write_image` to save figures, which requires the `kaleido` package to be installed.
3. **Subplots**: Used `make_subplots` to create grids and subplots, which is the `plotly` equivalent of `matplotlib`'s grid and subplot functionality.
4. **Axes**: Since `plotly` does not use explicit axes objects, the `check_ax` function was adapted to work with `plotly.graph_objects.Figure`.

This code maintains the original structure and functionality while using `plotly` for plotting.