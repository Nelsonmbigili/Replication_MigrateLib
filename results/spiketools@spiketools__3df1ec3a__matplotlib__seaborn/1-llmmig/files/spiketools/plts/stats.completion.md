### Explanation of Changes
To migrate the code from using `matplotlib` to `seaborn`, the following changes were made:
1. **Histogram Plotting**: The `plot_hist` function from `spiketools.plts.data` was replaced with `seaborn.histplot`, which is the equivalent function in `seaborn` for plotting histograms.
2. **Axis Management**: The `check_ax` function is retained to ensure compatibility with the existing application, but the actual plotting is now handled by `seaborn`.
3. **Customizations**: The `ax.axvline` and `ax.text` calls for adding vertical lines and text annotations remain unchanged, as they are compatible with `seaborn` (which uses `matplotlib` under the hood for these operations).
4. **Import Statement**: Added an import for `seaborn` (`import seaborn as sns`).

Below is the modified code.

---

### Modified Code
```python
"""Plots for statistical analyses and related visualizations."""

import seaborn as sns
from spiketools.plts.utils import check_ax, get_kwargs, savefig
from spiketools.plts.style import set_plt_kwargs

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_surrogates(surrogates, data_value=None, p_value=None, ax=None, **plt_kwargs):
    """Plot a distribution of surrogate data.

    Parameters
    ----------
    surrogates : 1d array
        The collection of values computed on surrogates.
    data_value : float, optional
        The statistic value of the real data, to draw on the plot.
    p_value : float, optional
        The p-value to print on the plot.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
        Custom kwargs: 'data_value_color', 'data_value_linestyle', 'data_value_lw'.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    custom_kwargs = ['data_value_color', 'data_value_linestyle', 'data_value_lw']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    # Use seaborn's histplot for plotting the histogram
    sns.histplot(surrogates, ax=ax, **plt_kwargs)

    if data_value is not None:
        ax.axvline(data_value,
                   color=custom_plt_kwargs.pop('data_value_color', 'k'),
                   linestyle=custom_plt_kwargs.pop('data_value_linestyle', 'dashed'),
                   lw=custom_plt_kwargs.pop('data_value_lw', 2))

    if p_value is not None:
        ax.text(0.15, 0.9, 'p={:4.4f}'.format(p_value),
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes)
```

### Key Notes
- The `sns.histplot` function is used to replace the `plot_hist` function. It integrates seamlessly with the existing `ax` object.
- The rest of the code remains unchanged to ensure compatibility with the larger application.
- The `seaborn` library is now required for this code to work.