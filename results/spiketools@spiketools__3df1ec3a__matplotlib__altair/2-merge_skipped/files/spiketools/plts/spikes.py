"""Plots for spikes."""

import numpy as np
import pandas as pd
import altair as alt

from spiketools.utils.options import get_avg_func, get_var_func
from spiketools.plts.utils import get_kwargs, savefig
from spiketools.plts.style import set_plt_kwargs

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_waveform(waveform, timestamps=None, average=None, shade=None, add_traces=False,
                  **plt_kwargs):
    """Plot a spike waveform.

    Parameters
    ----------
    waveform : 1d or 2d array
        Voltage values of the spike waveform(s).
        If 2d, should have shape [n_waveforms, n_timestamps].
    timestamps : 1d array, optional
        Timestamps corresponding to the waveform(s).
    average : {'mean', 'median'}, optional
        Averaging to apply to waveforms before plotting.
        If provided, this takes an average across an assumed 2d array of waveforms.
    shade : {'sem', 'std'} or 1d array, optional
        Measure of variance to compute and/or plot as shading.
    add_traces : bool, optional, default: False
        Whether to also plot individual waveform traces.
        Only applicable if `waveform` is a 2d array.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    if isinstance(shade, str):
        shade = get_var_func(shade)(waveform, 0)

    if isinstance(average, str):
        all_waveforms = waveform
        waveform = get_avg_func(average)(waveform, 0)

    xlabel = 'Time (s)'
    if timestamps is None:
        timestamps = np.arange(waveform.shape[-1])
        xlabel = 'Samples'

    # Prepare data for Altair
    data = pd.DataFrame({'Time': timestamps, 'Voltage': waveform})

    # Create the main line plot
    line_chart = alt.Chart(data).mark_line().encode(
        x=alt.X('Time', title=plt_kwargs.pop('xlabel', xlabel)),
        y=alt.Y('Voltage', title=plt_kwargs.pop('ylabel', 'Voltage'))
    ).properties(
        title=plt_kwargs.pop('title', 'Spike Waveform')
    )

    # Add individual traces if requested
    if add_traces:
        traces_data = pd.DataFrame(all_waveforms.T, columns=[f'Trace_{i}' for i in range(all_waveforms.shape[0])])
        traces_data['Time'] = timestamps
        traces_data = traces_data.melt(id_vars='Time', var_name='Trace', value_name='Voltage')

        traces_chart = alt.Chart(traces_data).mark_line(opacity=0.5).encode(
            x='Time',
            y='Voltage',
            color=alt.Color('Trace:N', legend=None)
        )
        line_chart += traces_chart

    # Add shading if requested
    if shade is not None:
        shade_data = pd.DataFrame({
            'Time': timestamps,
            'Lower': waveform - shade,
            'Upper': waveform + shade
        })
        shade_chart = alt.Chart(shade_data).mark_area(opacity=0.25).encode(
            x='Time',
            y='Lower',
            y2='Upper'
        )
        line_chart += shade_chart

    return line_chart


@savefig
@set_plt_kwargs
def plot_waveform_density(waveforms, timestamps=None, bins=(250, 50), cmap='viridis', **plt_kwargs):
def plot_waveforms3d(waveforms, timestamps=None, **plt_kwargs):
    """Plot waveforms on a 3D axis.

    Parameters
    ----------
    waveforms : 2d array
        Voltage values for the waveforms, with shape [n_waveforms, n_timestamps].
    timestamps : 1d array, optional
        Timestamps corresponding to the waveforms.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    plt.figure(figsize=plt_kwargs.pop('figsize', None))
    ax = plt.subplot(projection='3d')

    if timestamps is None:
        timestamps = np.arange(waveforms.shape[-1])

    ys = np.ones(waveforms.shape[1])
    for ind, waveform in enumerate(waveforms):
        ax.plot(timestamps, ys * ind, waveform)

    # Set axis view orientation and hide axes
    ax.view_init(None, None)
    ax.axis('off')
    ax.set(title=plt_kwargs.pop('title', 'Spike Waveforms'))


@savefig
@set_plt_kwargs
def plot_waveform_density(waveforms, timestamps=None, bins=(250, 50), cmap='viridis',
                          ax=None, **plt_kwargs):
    """Plot a heatmap of waveform density, created as a 2d histogram of spike waveforms.

    Parameters
    ----------
    waveforms : 2d array
        Voltage values for the waveforms, with shape [n_waveforms, n_timestamps].
    timestamps : 1d array, optional
        Timestamps corresponding to the waveforms.
    bins : tuple of (int, int), optional, default: (250, 50)
        Bin definition to use to create the figure.
    cmap : str, optional, default: 'viridis'
        Colormap to use for the figure.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    xlabel = 'Time (s)'
    if timestamps is None:
        timestamps = np.arange(waveforms.shape[-1])
        xlabel = 'Samples'
    timestamps = np.vstack([timestamps] * waveforms.shape[0])

    # Prepare data for Altair
    data = pd.DataFrame({'Time': timestamps.flatten(), 'Voltage': waveforms.flatten()})

    # Create a 2D histogram (heatmap)
    heatmap = alt.Chart(data).mark_rect().encode(
        x=alt.X('Time:Q', bin=alt.Bin(maxbins=bins[0]), title=plt_kwargs.pop('xlabel', xlabel)),
        y=alt.Y('Voltage:Q', bin=alt.Bin(maxbins=bins[1]), title=plt_kwargs.pop('ylabel', 'Voltage')),
        color=alt.Color('count()', scale=alt.Scale(scheme=cmap), title='Density')
    ).properties(
        title=plt_kwargs.pop('title', 'Spike Histogram')
    )

    return heatmap


@savefig
@set_plt_kwargs
def plot_isis(isis, bins=None, range=None, density=False, **plt_kwargs):
    """Plot a distribution of ISIs.

    Parameters
    ----------
    isis : 1d array
        Interspike intervals.
    bins : int or list, optional
        Bin definition, either a number of bins to use, or bin definitions.
    range : tuple, optional
        Range of the data to plot.
    density : bool, optional, default: False
        Whether to draw a probability density.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Prepare data for Altair
    data = pd.DataFrame({'ISI': isis})

    # Create a histogram
    hist = alt.Chart(data).mark_bar().encode(
        x=alt.X('ISI:Q', bin=alt.Bin(maxbins=bins), title=plt_kwargs.pop('xlabel', 'Time')),
        y=alt.Y('count()', title='Count')
    ).properties(
        title=plt_kwargs.pop('title', 'ISIs')
    )

    return hist


@savefig
@set_plt_kwargs
def plot_firing_rates(rates, **plt_kwargs):
    """Plot firing rates for a group of neurons.

    Parameters
    ----------
    rates : list of float
        Firing rates.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    # Prepare data for Altair
    data = pd.DataFrame({'Unit': [f'U{ind}' for ind in range(len(rates))], 'Rate': rates})

    # Create a bar plot
    bar_chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Unit:N', title=plt_kwargs.pop('xlabel', 'Units')),
        y=alt.Y('Rate:Q', title=plt_kwargs.pop('ylabel', 'Firing Rate (Hz)'))
    ).properties(
        title=plt_kwargs.pop('title', 'Firing Rates of all Units')
    )

    return bar_chart