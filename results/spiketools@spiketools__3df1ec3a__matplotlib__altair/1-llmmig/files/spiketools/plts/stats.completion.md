### Explanation of Changes
To migrate the code from `matplotlib` to `altair`, the following changes were made:
1. **Histogram Plotting**: The `plot_hist` function from `spiketools.plts.data` was replaced with an equivalent `altair.Chart` histogram.
2. **Vertical Line for `data_value`**: The `ax.axvline` method was replaced with an `altair.Chart` rule mark (`mark_rule`) to draw a vertical line.
3. **Text Annotation for `p_value`**: The `ax.text` method was replaced with an `altair.Chart` text mark (`mark_text`) to display the p-value.
4. **Axis Handling**: Since `altair` does not use `matplotlib`'s `Axes` objects, the `check_ax` function was removed, and the `ax` parameter is no longer used.
5. **Keyword Arguments**: The `plt_kwargs` were adapted to work with `altair`'s configuration options, such as `color`, `strokeDash`, and `strokeWidth`.

Below is the modified code using `altair`:

---

### Modified Code
```python
"""Plots for statistical analyses and related visualizations."""

from spiketools.plts.utils import get_kwargs, savefig
import altair as alt
import pandas as pd

###################################################################################################
###################################################################################################

@savefig
def plot_surrogates(surrogates, data_value=None, p_value=None, **plt_kwargs):
    """Plot a distribution of surrogate data.

    Parameters
    ----------
    surrogates : 1d array
        The collection of values computed on surrogates.
    data_value : float, optional
        The statistic value of the real data, to draw on the plot.
    p_value : float, optional
        The p-value to print on the plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
        Custom kwargs: 'data_value_color', 'data_value_linestyle', 'data_value_lw'.
    """

    # Convert surrogates to a DataFrame for Altair
    surrogates_df = pd.DataFrame({'surrogates': surrogates})

    # Extract custom kwargs for data_value styling
    custom_kwargs = ['data_value_color', 'data_value_linestyle', 'data_value_lw']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    # Create the histogram
    hist = alt.Chart(surrogates_df).mark_bar().encode(
        alt.X('surrogates:Q', bin=alt.Bin(maxbins=30), title='Surrogates'),
        alt.Y('count()', title='Frequency')
    )

    # Add a vertical line for the data_value, if provided
    if data_value is not None:
        data_value_line = alt.Chart(pd.DataFrame({'data_value': [data_value]})).mark_rule(
            color=custom_plt_kwargs.pop('data_value_color', 'black'),
            strokeDash=custom_plt_kwargs.pop('data_value_linestyle', [4, 2]),
            strokeWidth=custom_plt_kwargs.pop('data_value_lw', 2)
        ).encode(
            x='data_value:Q'
        )
        hist += data_value_line

    # Add text annotation for the p-value, if provided
    if p_value is not None:
        p_value_text = alt.Chart(pd.DataFrame({'p_value': [f'p={p_value:4.4f}']})).mark_text(
            align='left',
            baseline='top',
            dx=10,
            dy=-10
        ).encode(
            text='p_value:N'
        ).properties(
            width=400,
            height=300
        )
        hist += p_value_text

    # Return the final Altair chart
    return hist
```

---

### Key Notes
1. **Altair Data Handling**: Altair requires data to be in a tabular format (e.g., a Pandas DataFrame). The `surrogates` array was converted to a DataFrame for this purpose.
2. **Custom Styling**: The `data_value_color`, `data_value_linestyle`, and `data_value_lw` were mapped to Altair's `color`, `strokeDash`, and `strokeWidth` properties, respectively.
3. **Text Positioning**: The `p_value` text annotation was positioned using `dx` and `dy` offsets relative to the chart.

This code now uses `altair` for visualization while maintaining the original functionality and structure.