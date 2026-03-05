"""Plots for statistical analyses and related visualizations."""

from spiketools.plts.data import plot_hist
from spiketools.plts.utils import check_ax, get_kwargs, savefig
from spiketools.plts.style import set_plt_kwargs
import plotly.graph_objects as go

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

    # Create a Plotly figure
    fig = go.Figure()

    custom_kwargs = ['data_value_color', 'data_value_linestyle', 'data_value_lw']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    # Plot histogram using Plotly
    fig.add_trace(go.Histogram(x=surrogates, name='Surrogates', opacity=0.75))

    if data_value is not None:
        fig.add_shape(type="line",
                      x0=data_value, y0=0, x1=data_value, y1=1,
                      line=dict(color=custom_plt_kwargs.pop('data_value_color', 'black'),
                                dash=custom_plt_kwargs.pop('data_value_linestyle', 'dash'),
                                width=custom_plt_kwargs.pop('data_value_lw', 2)))

    if p_value is not None:
        fig.add_annotation(x=0.15, y=0.9, text='p={:4.4f}'.format(p_value),
                           showarrow=False, xref="paper", yref="paper",
                           font=dict(size=12))

    # Show the figure
    fig.show()
