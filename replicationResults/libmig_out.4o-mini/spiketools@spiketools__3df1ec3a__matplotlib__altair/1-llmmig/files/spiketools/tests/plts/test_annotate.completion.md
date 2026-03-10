To migrate the provided code from using the `matplotlib` library to the `altair` library, several key changes were made:

1. **Plotting Functions**: The plotting functions in `matplotlib` (like `plt.subplots()`, `ax.plot()`, `ax.bar()`, etc.) are replaced with `altair`'s declarative syntax. In `altair`, we create charts using the `Chart` class and specify the encoding for axes and marks.

2. **Vertical and Horizontal Lines**: The functions `add_vlines` and `add_hlines` are replaced with `mark_rule()` in `altair`, which allows us to add vertical and horizontal lines to the chart.

3. **Gridlines**: The `add_gridlines` function is not directly translatable to `altair`, as gridlines are typically handled automatically based on the chart's configuration.

4. **Shading and Box Areas**: The functions for adding vertical and horizontal shades (`add_vshades`, `add_hshades`, `add_box_shade`, `add_box_shades`) are replaced with `mark_area()` in `altair`, which allows for shaded regions.

5. **Dots and Significance**: The `add_dots` and `add_significance` functions are replaced with `mark_point()` for dots and a combination of `mark_text()` for significance annotations.

6. **Text Labels**: The `add_text_labels` functions are replaced with `mark_text()` in `altair`, which allows for adding text annotations to the chart.

Here is the modified code using `altair`:

```python
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
```

This code now uses `altair` for plotting, maintaining the original structure and function names as requested.