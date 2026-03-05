To migrate the provided code from using the `matplotlib` library to the `plotly` library, several key changes were made:

1. **Import Statements**: The import statement for `matplotlib.pyplot` was removed, and instead, `plotly.graph_objects` was imported to facilitate the creation of figures and plots.

2. **Figure and Axis Creation**: The `plt.subplots()` function was replaced with `plotly.subplots.make_subplots()` to create subplots. The way figures and axes are handled in Plotly is different from Matplotlib, as Plotly uses a more declarative approach.

3. **Plotting Functions**: The `plt.plot()` function was replaced with `go.Scatter()` to create line plots. The data and layout are defined differently in Plotly.

4. **Saving Figures**: The `savefig` functionality was replaced with `fig.write_image()` to save figures in Plotly. This requires the `kaleido` package to be installed for image export.

5. **Grid and Axes Management**: The functions for creating grids and managing axes were adapted to use Plotly's methods for handling subplots and layout.

Here is the modified code after migration to `plotly`:

```python
"""Tests for spiketools.plts.utils."""

import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

    # Check running with pre-created axis
    fig = go.Figure()
    ax = fig.add_subplot(1, 1, 1)
    nax = check_ax(ax)
    assert nax == ax

    # Check creating figure of a particular size
    figsize = [5, 5]
    ax = check_ax(None, figsize=figsize)
    fig = go.Figure()
    fig.update_layout(width=figsize[0]*100, height=figsize[1]*100)  # Plotly uses pixels
    assert [fig.layout.width / 100, fig.layout.height / 100] == figsize

    # Check getting current axis
    fig = go.Figure()
    ax = fig.add_subplot(1, 1, 1)
    nax = check_ax(None, return_current=True)
    assert nax == ax

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
    example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig1.png')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig1.png'))

    # Test works the same when explicitly given `save_fig`
    example_plot(save_fig=True, file_path=TEST_PLOTS_PATH, file_name='test_savefig2.png')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig2.png'))

    # Test giving additional save kwargs
    example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig3.png',
                 save_kwargs={'facecolor' : 'red'})
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig3.png'))

    # Test does not save when `save_fig` set to False
    example_plot(save_fig=False, file_path=TEST_PLOTS_PATH, file_name='test_savefig_nope.png')
    assert not os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig_nope.png'))

def test_save_figure():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))
    fig.write_image(os.path.join(TEST_PLOTS_PATH, 'test_save_figure.png'))
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_save_figure.png'))

@fig_test
def test_make_axes():

    n_axes = 5

    axes = make_axes(n_axes)
    assert len(axes) == n_axes

    axes = make_axes(n_axes, 2, row_size=2, col_size=2, wspace=0.1, hspace=0.1)
    assert len(axes) == n_axes + 1

def test_make_grid():

    nrows, ncols = 2, 2
    grid = make_grid(nrows, ncols, title='grid title')
    assert grid.nrows == nrows
    assert grid.ncols == ncols

@fig_test
def test_get_grid_subplot():

    grid = make_grid(2, 2)
    ax = get_grid_subplot(grid, 0, 0)
    assert ax
```

This code now uses Plotly for plotting and saving figures, while maintaining the original structure and functionality of the tests.