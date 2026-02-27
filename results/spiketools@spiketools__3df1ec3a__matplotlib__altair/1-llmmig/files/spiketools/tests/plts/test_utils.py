"""Tests for spiketools.plts.utils."""

import os
import altair as alt
import pandas as pd

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

    # Check creating figure of a particular size
    figsize = [5, 5]
    ax = check_ax(None, figsize=figsize)
    assert ax.width == figsize[0] * 100 and ax.height == figsize[1] * 100

def test_get_kwargs():

    kwargs = {'title': 'title', 'xlabel': 'xlabel', 'lw': 12}
    out = get_kwargs(kwargs, SET_KWARGS)
    for arg in ['title', 'xlabel']:
        assert arg in out
        assert arg not in kwargs
    for arg in ['lw']:
        assert arg not in out
        assert arg in kwargs

def test_get_attr_kwargs():

    kwargs = {'title_color': 'red', 'xlabel': 'xlabel', 'lw': 12}
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
        data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
        chart = alt.Chart(data).mark_line().encode(x='x', y='y')
        return chart

    # Test defaults to saving given file path & name
    chart = example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig1.html')
    chart.save(os.path.join(TEST_PLOTS_PATH, 'test_savefig1.html'))
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig1.html'))

    # Test works the same when explicitly given `save_fig`
    chart = example_plot(save_fig=True, file_path=TEST_PLOTS_PATH, file_name='test_savefig2.html')
    chart.save(os.path.join(TEST_PLOTS_PATH, 'test_savefig2.html'))
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig2.html'))

    # Test does not save when `save_fig` set to False
    chart = example_plot(save_fig=False, file_path=TEST_PLOTS_PATH, file_name='test_savefig_nope.html')
    assert not os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig_nope.html'))

def test_save_figure():

    data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    chart.save(os.path.join(TEST_PLOTS_PATH, 'test_save_figure.html'))
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_save_figure.html'))

@fig_test
def test_make_axes():

    n_axes = 5

    # Create multiple charts (axes equivalent in Altair)
    data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
    charts = [alt.Chart(data).mark_line().encode(x='x', y='y') for _ in range(n_axes)]
    assert len(charts) == n_axes

    # Combine charts into a grid layout
    combined_chart = alt.vconcat(*charts)
    assert combined_chart

def test_make_grid():

    nrows, ncols = 2, 2
    data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
    charts = [alt.Chart(data).mark_line().encode(x='x', y='y') for _ in range(nrows * ncols)]
    grid = alt.vconcat(*[alt.hconcat(*charts[i:i + ncols]) for i in range(0, len(charts), ncols)])
    assert grid

@fig_test
def test_get_grid_subplot():

    data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
    charts = [alt.Chart(data).mark_line().encode(x='x', y='y') for _ in range(4)]
    grid = alt.vconcat(*[alt.hconcat(*charts[i:i + 2]) for i in range(0, len(charts), 2)])
    assert grid
