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
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    vlines = alt.Chart(pd.DataFrame({'x': [1.5, 2.5, 3.5]})).mark_rule(color='black').encode(x='x')
    chart = base + vlines
    chart.show()

@plot_test
def test_add_hlines():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    hlines = alt.Chart(pd.DataFrame({'y': [1.5, 2.5, 3.5]})).mark_rule(color='black').encode(y='y')
    chart = base + hlines
    chart.show()

@plot_test
def test_add_gridlines():

    data = pd.DataFrame({'x': [0, 2], 'y': [0, 2]})
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    bins = [0.5, 1.5]
    grid_x = alt.Chart(pd.DataFrame({'x': bins})).mark_rule(strokeDash=[5, 5]).encode(x='x')
    grid_y = alt.Chart(pd.DataFrame({'y': bins})).mark_rule(strokeDash=[5, 5]).encode(y='y')

    chart = base + grid_x + grid_y
    chart.show()

@plot_test
def test_add_vshades():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    vshades = alt.Chart(pd.DataFrame({'x1': [2.0, 3.5], 'x2': [3.0, 3.75]})).mark_rect(color='red', opacity=0.3).encode(
        x='x1:Q', x2='x2:Q')
    chart = base + vshades
    chart.show()

@plot_test
def test_add_hshades():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    hshades = alt.Chart(pd.DataFrame({'y1': [2.0, 3.5], 'y2': [3.0, 3.75]})).mark_rect(color='red', opacity=0.3).encode(
        y='y1:Q', y2='y2:Q')
    chart = base + hshades
    chart.show()

@plot_test
def test_add_box_shade():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    box_shade = alt.Chart(pd.DataFrame({'x1': [1.5], 'x2': [2.5], 'y1': [0], 'y2': [2]})).mark_rect(color='blue', opacity=0.3).encode(
        x='x1:Q', x2='x2:Q', y='y1:Q', y2='y2:Q')
    chart = base + box_shade
    chart.show()

@plot_test
def test_add_box_shades():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    box_shades = alt.Chart(pd.DataFrame({'x1': [1.5, 2.5], 'x2': [2.5, 3.5], 'y1': [1.5, 2.5], 'y2': [2.5, 3.5]})).mark_rect(color='blue', opacity=0.3).encode(
        x='x1:Q', x2='x2:Q', y='y1:Q', y2='y2:Q')
    chart = base + box_shades
    chart.show()

@plot_test
def test_add_dots():

    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]})
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    dots = alt.Chart(pd.DataFrame({'x': [1, 2, 2.5], 'y': [2, 3, 2.5], 'color': ['blue', 'blue', 'red']})).mark_point().encode(
        x='x', y='y', color='color:N')
    chart = base + dots
    chart.show()

@plot_test
def test_add_significance():

    x_values = [1, 2, 3, 4]
    stats = [1., 0.01, 0.5, 1.]

    data = pd.DataFrame({'x': x_values, 'y': stats})
    base = alt.Chart(data).mark_line().encode(x='x', y='y')

    significance = alt.Chart(data).mark_text(dy=-10).encode(
        x='x', y='y', text=alt.Text('y:Q', format='.2f'))
    chart = base + significance
    chart.show()

@plot_test
def test_add_text_labels_x():

    data = pd.DataFrame({'category': ['A', 'B', 'C', 'D'], 'value': [15, 12, 32, 22]})
    chart = alt.Chart(data).mark_bar().encode(x='category', y='value')

    labels = chart.mark_text(dy=-10).encode(text='value:Q')
    chart = chart + labels
    chart.show()

@plot_test
def test_add_text_labels_y():

    data = pd.DataFrame({'category': ['A', 'B', 'C', 'D'], 'value': [15, 12, 32, 22]})
    chart = alt.Chart(data).mark_bar().encode(y='category', x='value')

    labels = chart.mark_text(dx=10).encode(text='value:Q')
    chart = chart + labels
    chart.show()
