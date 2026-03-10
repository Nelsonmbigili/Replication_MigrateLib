"""Tests for spiketools.plts.annotate"""

import numpy as np
import altair as alt
import pandas as pd

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

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    vlines = alt.Chart(pd.DataFrame({'x': [1.5, 2.5, 3.5]})).mark_rule().encode(x='x')
    chart = chart + vlines
    return chart

@plot_test
def test_add_hlines():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    hlines = alt.Chart(pd.DataFrame({'y': [1.5, 2.5, 3.5]})).mark_rule().encode(y='y')
    chart = chart + hlines
    return chart

@plot_test
def test_add_gridlines():

    data = pd.DataFrame({'x': [0, 2], 'y': [0, 2]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    return chart

@plot_test
def test_add_vshades():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    vshades = alt.Chart(pd.DataFrame({'start': [2.0], 'end': [3.0]})).mark_area(opacity=0.3).encode(x='start:Q', x2='end:Q')
    chart = chart + vshades
    return chart

@plot_test
def test_add_hshades():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    hshades = alt.Chart(pd.DataFrame({'start': [2.0], 'end': [3.0]})).mark_area(opacity=0.3).encode(y='start:Q', y2='end:Q')
    chart = chart + hshades
    return chart

@plot_test
def test_add_box_shade():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    box_shade = alt.Chart(pd.DataFrame({'start': [1.5], 'end': [2.5], 'y': [2]})).mark_area(opacity=0.3).encode(x='start:Q', x2='end:Q', y='y:Q')
    chart = chart + box_shade
    return chart

@plot_test
def test_add_box_shades():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    box_shades = alt.Chart(pd.DataFrame({'start': [1.5, 2.5], 'end': [1.5, 2.5]})).mark_area(opacity=0.3).encode(x='start:Q', x2='end:Q', y='y:Q')
    chart = chart + box_shades
    return chart

@plot_test
def test_add_dots():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    dots = alt.Chart(pd.DataFrame({'x': [1, 2], 'y': [2, 3]})).mark_point(color='red').encode(x='x', y='y')
    chart = chart + dots
    return chart

@plot_test
def test_add_significance():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 0.01, 0.5, 1.]})
    chart = alt.Chart(data).mark_line().encode(x='x', y='y')
    significance = alt.Chart(pd.DataFrame({'x': [1, 2, 3, 4], 'y': [0.5]})).mark_text(text='*').encode(x='x', y='y')
    chart = chart + significance
    return chart

@plot_test
def test_add_text_labels_x():

    data = pd.DataFrame({'category': ['A', 'B', 'C', 'D'], 'value': [15, 12, 32, 22]})
    chart = alt.Chart(data).mark_bar().encode(x='category', y='value')
    text = chart.mark_text(dy=-5).encode(text='value:Q')
    chart = chart + text
    return chart

@plot_test
def test_add_text_labels_y():

    data = pd.DataFrame({'category': ['A', 'B', 'C', 'D'], 'value': [15, 12, 32, 22]})
    chart = alt.Chart(data).mark_bar().encode(y='category', x='value')
    text = chart.mark_text(dx=5).encode(text='value:Q')
    chart = chart + text
    return chart
