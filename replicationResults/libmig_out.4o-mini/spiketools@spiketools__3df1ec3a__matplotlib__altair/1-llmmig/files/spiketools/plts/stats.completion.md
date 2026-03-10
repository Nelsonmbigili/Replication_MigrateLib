### Explanation of Changes
To migrate the code from using `matplotlib` to `altair`, several key changes were made:

1. **Plotting Functions**: The `plot_hist` function from `spiketools` was replaced with Altair's `Chart` and `mark_bar` for histogram plotting. Altair uses a declarative approach to create visualizations.
  
2. **Axis and Lines**: Instead of using `ax.axvline` to draw a vertical line for the data value, Altair's `mark_rule` was used to create a vertical line.

3. **Text Annotations**: The text annotation was replaced with Altair's `mark_text` to display the p-value on the plot.

4. **Data Handling**: Altair requires data to be in a specific format (usually a DataFrame), so the surrogate data was converted into a DataFrame for plotting.

5. **Figure Saving**: The `savefig` decorator was retained, but the way the figure is displayed or saved is handled differently in Altair.

Here is the modified code:

```python
"""Plots for statistical analyses and related visualizations."""

import altair as alt
import pandas as pd
from spiketools.plts.data import plot_hist
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

    # Convert surrogates to a DataFrame for Altair
    df = pd.DataFrame({'surrogates': surrogates})

    # Create histogram using Altair
    histogram = alt.Chart(df).mark_bar().encode(
        alt.X('surrogates:Q', bin=True),
        alt.Y('count():Q')
    ).properties(width=plt_kwargs.get('figsize', (400, 300))[0], height=plt_kwargs.get('figsize', (400, 300))[1])

    # Add a vertical line for the data value if provided
    if data_value is not None:
        line = alt.Chart(pd.DataFrame({'data_value': [data_value]})).mark_rule(
            color=custom_plt_kwargs.pop('data_value_color', 'black'),
            strokeDash=[5, 5]
        ).encode(
            x='data_value:Q'
        )
        histogram = histogram + line

    # Add text for p-value if provided
    if p_value is not None:
        text = alt.Chart(pd.DataFrame({'p_value': [p_value]})).mark_text(
            align='center',
            baseline='middle',
            dy=-10
        ).encode(
            x=alt.value(0.15),  # x position in normalized coordinates
            y=alt.value(0.9),   # y position in normalized coordinates
            text='p_value:Q'
        )
        histogram = histogram + text

    # Display the plot
    return histogram
``` 

This code now uses Altair for plotting while maintaining the original function's structure and parameters.