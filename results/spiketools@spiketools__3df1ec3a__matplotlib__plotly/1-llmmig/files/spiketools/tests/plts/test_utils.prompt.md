The following Python code currently uses the library "matplotlib" version 3.10.1.
Migrate this code to use the library "plotly" version 6.0.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "matplotlib" to "plotly".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "matplotlib" and "plotly".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""Tests for spiketools.plts.utils."""

import os

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
    _, ax = plt.subplots()
    nax = check_ax(ax)
    assert nax == ax

    # Check creating figure of a particular size
    figsize = [5, 5]
    ax = check_ax(None, figsize=figsize)
    fig = plt.gcf()
    assert list(fig.get_size_inches()) == figsize

    # Check getting current axis
    _, ax = plt.subplots()
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
        plt.plot([1, 2], [3, 4])

    # Test defaults to saving given file path & name
    example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig1.pdf')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig1.pdf'))

    # Test works the same when explicitly given `save_fig`
    example_plot(save_fig=True, file_path=TEST_PLOTS_PATH, file_name='test_savefig2.pdf')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig2.pdf'))

    # Test giving additional save kwargs
    example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig3.pdf',
                 save_kwargs={'facecolor' : 'red'})
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig3.pdf'))

    # Test does not save when `save_fig` set to False
    example_plot(save_fig=False, file_path=TEST_PLOTS_PATH, file_name='test_savefig_nope.pdf')
    assert not os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig_nope.pdf'))

def test_save_figure():

    plt.plot([1, 2], [3, 4])
    save_figure(file_name='test_save_figure.pdf', file_path=TEST_PLOTS_PATH)
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_save_figure.pdf'))

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