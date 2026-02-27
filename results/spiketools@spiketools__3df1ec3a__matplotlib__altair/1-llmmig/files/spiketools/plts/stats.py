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
