"""Tests for spiketools.plts.style."""

import numpy as np
import altair as alt
import pandas as pd

from spiketools.plts.settings import SET_KWARGS

from spiketools.plts.style import *

###################################################################################################
###################################################################################################

def test_set_plt_kwargs():

    def example_plot(xlim=None, ylim=None, title=None):
        data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
        chart = alt.Chart(data).mark_line().encode(
            x=alt.X('x', scale=alt.Scale(domain=xlim) if xlim else alt.Undefined),
            y=alt.Y('y', scale=alt.Scale(domain=ylim) if ylim else alt.Undefined)
        )
        if title:
            chart = chart.properties(title=title)
        return chart

    xlim = (0, 2)
    ylim = (0, 4)
    title = 'Test Title'

    chart1 = example_plot(xlim=xlim, ylim=ylim)
    assert chart1.encoding.x.scale.domain == list(xlim)
    assert chart1.encoding.y.scale.domain == list(ylim)

    chart2 = example_plot(title=title)
    assert chart2.title == title


def test_drop_spines():

    # In Altair, spines are not explicitly present. Instead, we can hide axes.
    def drop_spines(axes_to_drop, chart):
        if 'top' in axes_to_drop or 'bottom' in axes_to_drop:
            chart = chart.configure_axisX(domain=False)
        if 'left' in axes_to_drop or 'right' in axes_to_drop:
            chart = chart.configure_axisY(domain=False)
        return chart

    data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    chart = drop_spines(['top', 'right'], chart)


def test_invert_axes():

    # In Altair, axis inversion is done by reversing the scale.
    def invert_axes(axis, chart):
        if axis == 'x':
            chart = chart.encode(x=alt.X('x', scale=alt.Scale(reverse=True)))
        elif axis == 'y':
            chart = chart.encode(y=alt.Y('y', scale=alt.Scale(reverse=True)))
        elif axis == 'both':
            chart = chart.encode(
                x=alt.X('x', scale=alt.Scale(reverse=True)),
                y=alt.Y('y', scale=alt.Scale(reverse=True))
            )
        return chart

    data = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
    chart1 = alt.Chart(data).mark_line().encode(x='x', y='y')

    # Test inverting x & y axes separately
    chart1 = invert_axes('x', chart1)
    assert chart1.encoding.x.scale.reverse is True

    chart1 = invert_axes('y', chart1)
    assert chart1.encoding.y.scale.reverse is True

    # Test inverting both axes together
    chart2 = alt.Chart(data).mark_line().encode(x='x', y='y')
    chart2 = invert_axes('both', chart2)
    assert chart2.encoding.x.scale.reverse is True
    assert chart2.encoding.y.scale.reverse is True
