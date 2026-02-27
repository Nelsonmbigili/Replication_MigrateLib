"""Tests for spiketools.plts.style."""

import numpy as np
import plotly.graph_objects as go

from spiketools.plts.settings import SET_KWARGS

from spiketools.plts.style import *

###################################################################################################
###################################################################################################

def test_set_plt_kwargs():

    @set_plt_kwargs
    def example_plot():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))
        return fig

    xlim = (0, 2)
    ylim = (0, 4)
    title = 'Test Title'

    fig = example_plot(xlim=xlim, ylim=ylim)
    fig.update_layout(xaxis=dict(range=xlim), yaxis=dict(range=ylim))
    assert fig.layout.xaxis.range == list(xlim)
    assert fig.layout.yaxis.range == list(ylim)

    fig = example_plot(title=title)
    fig.update_layout(title=title)
    assert fig.layout.title.text == title


def test_drop_spines():

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))

    # Drop spines by hiding the axes
    drop_spines(['top', 'right'], fig)


def test_invert_axes():

    # test inverting x & y axes separately
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))

    invert_axes('x', fig1)
    assert fig1.layout.xaxis.autorange == 'reversed'

    invert_axes('y', fig1)
    assert fig1.layout.yaxis.autorange == 'reversed'

    # test inverting both axes together
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))
    invert_axes('both', fig2)
    assert fig2.layout.xaxis.autorange == 'reversed'
    assert fig2.layout.yaxis.autorange == 'reversed'
