### Explanation of Changes:
To migrate the code from using `matplotlib` to `seaborn`, the following changes were made:
1. **Plotting Functions**: Replaced `plt.plot` with `sns.lineplot` for line plots, as `seaborn` provides high-level APIs for such visualizations.
2. **Subplots**: Replaced `plt.subplots()` with `sns.set_theme()` and `sns.axes_style()` to configure the style and axes. `seaborn` does not directly provide a `subplots` function, so we use `matplotlib`'s `subplots` for creating axes but apply `seaborn` styles.
3. **Spine Management**: `seaborn` does not have a direct equivalent for `drop_spines`, so we retained the logic for spine removal using `matplotlib`'s `ax.spines` but ensured compatibility with `seaborn`'s styling.
4. **Axis Inversion**: Axis inversion (`invert_axes`) is handled using `matplotlib`'s `ax.invert_xaxis()` and `ax.invert_yaxis()` since `seaborn` relies on `matplotlib` for such low-level operations.

### Modified Code:
```python
"""Tests for spiketools.plts.style."""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from spiketools.plts.settings import SET_KWARGS

from spiketools.plts.style import *

###################################################################################################
###################################################################################################

def test_set_plt_kwargs():

    @set_plt_kwargs
    def example_plot():
        sns.lineplot(x=[1, 2], y=[3, 4])

    xlim = (0, 2)
    ylim = (0, 4)
    title = 'Test Title'

    example_plot(xlim=xlim, ylim=ylim)
    assert plt.gca().get_xlim() == xlim
    assert plt.gca().get_ylim() == ylim

    example_plot(title=title)
    assert plt.gca().get_title() == title


def test_drop_spines():

    sns.set_theme()  # Apply seaborn theme
    _, ax = plt.subplots()
    drop_spines(['top', 'right'], ax)

def test_invert_axes():

    sns.set_theme()  # Apply seaborn theme

    # test inverting x & y axes separately
    _, ax1 = plt.subplots()
    sns.lineplot(x=[1, 2], y=[3, 4], ax=ax1)

    invert_axes('x', ax1)
    assert ax1.get_xlim()[0] > ax1.get_xlim()[1]

    invert_axes('y', ax1)
    assert ax1.get_ylim()[0] > ax1.get_ylim()[1]

    # test inverting both axes together
    _, ax2 = plt.subplots()
    sns.lineplot(x=[1, 2], y=[3, 4], ax=ax2)
    invert_axes('both', ax2)
    assert ax2.get_xlim()[0] > ax2.get_xlim()[1]
    assert ax2.get_ylim()[0] > ax2.get_ylim()[1]
```

### Key Notes:
- `seaborn` is built on top of `matplotlib`, so some low-level operations (like spine removal and axis inversion) still rely on `matplotlib`'s API.
- The `sns.lineplot` function is used for line plots, which is the closest equivalent to `plt.plot`.
- `sns.set_theme()` is used to apply `seaborn`'s default styling globally, ensuring consistency with the library's design philosophy.