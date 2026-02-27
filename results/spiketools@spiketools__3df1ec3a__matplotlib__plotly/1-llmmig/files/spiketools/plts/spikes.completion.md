### Explanation of Changes
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. **Import Changes**: Removed `matplotlib.pyplot` and replaced it with `plotly.graph_objects` (`go`) and `plotly.express` (`px`) where necessary.
2. **Axis Handling**: Removed `check_ax` and `ax` handling since `plotly` does not use explicit axis objects. Instead, plots are created directly using `plotly` objects.
3. **Plotting Functions**: Replaced `matplotlib` plotting functions (`plot`, `fill_between`, `hist2d`, etc.) with equivalent `plotly` methods (`go.Scatter`, `go.Figure`, `go.Histogram2d`, etc.).
4. **3D Plotting**: Used `go.Scatter3d` for 3D plotting instead of `matplotlib`'s 3D axis.
5. **Heatmap**: Used `go.Histogram2d` for 2D histograms instead of `matplotlib`'s `hist2d`.
6. **Bar and Histogram Plots**: Replaced `plot_bar` and `plot_hist` with `plotly` equivalents (`go.Bar` and `go.Histogram`).
7. **Styling and Titles**: Incorporated `plotly`'s `layout` for styling, titles, and axis labels.

Below is the modified code.

---

### Modified Code
```python
"""Plots for spikes."""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from spiketools.utils.options import get_avg_func, get_var_func
from spiketools.plts.data import plot_bar, plot_hist, plot_lines
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
        Custom kwargs: 'traces_lw', 'traces_alpha', 'shade_alpha'.
    """

    custom_kwargs = ['traces_lw', 'traces_alpha', 'shade_alpha']
    custom_plt_kwargs = get_kwargs(plt_kwargs, custom_kwargs)

    if isinstance(shade, str):
        shade = get_var_func(shade)(waveform, 0)

    if isinstance(average, str):
        all_waveforms = waveform
        waveform = get_avg_func(average)(waveform, 0)

    xlabel = 'Time (s)'
    if timestamps is None:
        timestamps = np.arange(waveform.shape[-1])
        xlabel = 'Samples'

    fig = go.Figure()

    # Plot the main waveform
    fig.add_trace(go.Scatter(x=timestamps, y=waveform, mode='lines',
                             name='Waveform', line=dict(color='blue')))

    # Add individual traces if requested
    if add_traces:
        for trace in all_waveforms:
            fig.add_trace(go.Scatter(x=timestamps, y=trace, mode='lines',
                                     line=dict(width=custom_plt_kwargs.pop('traces_lw', 1),
                                               color='blue'),
                                     opacity=custom_plt_kwargs.pop('traces_alpha', 0.5),
                                     showlegend=False))

    # Add shading if provided
    if shade is not None:
        fig.add_trace(go.Scatter(x=np.concatenate([timestamps, timestamps[::-1]]),
                                 y=np.concatenate([waveform - shade, (waveform + shade)[::-1]]),
                                 fill='toself', fillcolor='rgba(0,0,255,0.25)',
                                 line=dict(color='rgba(255,255,255,0)'), showlegend=False))

    # Update layout
    fig.update_layout(title=plt_kwargs.pop('title', 'Spike Waveform'),
                      xaxis_title=plt_kwargs.pop('xlabel', xlabel),
                      yaxis_title=plt_kwargs.pop('ylabel', 'Voltage'))
    fig.show()


@savefig
@set_plt_kwargs
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

    if timestamps is None:
        timestamps = np.arange(waveforms.shape[-1])

    ys = np.arange(waveforms.shape[0])

    fig = go.Figure()

    for ind, waveform in enumerate(waveforms):
        fig.add_trace(go.Scatter3d(x=timestamps, y=np.full_like(timestamps, ys[ind]), z=waveform,
                                   mode='lines', line=dict(color='blue')))

    # Update layout
    fig.update_layout(scene=dict(
        xaxis_title='Time (s)',
        yaxis_title='Waveform Index',
        zaxis_title='Voltage'),
        title=plt_kwargs.pop('title', 'Spike Waveforms'))
    fig.show()


@savefig
@set_plt_kwargs
def plot_waveform_density(waveforms, timestamps=None, bins=(250, 50), cmap='viridis', **plt_kwargs):
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
    """

    if timestamps is None:
        timestamps = np.arange(waveforms.shape[-1])
    timestamps = np.vstack([timestamps] * waveforms.shape[0])

    fig = go.Figure(go.Histogram2d(x=timestamps.flatten(), y=waveforms.flatten(),
                                   xbins=dict(size=bins[0]), ybins=dict(size=bins[1]),
                                   colorscale=cmap))

    # Update layout
    fig.update_layout(title=plt_kwargs.pop('title', 'Spike Histogram'),
                      xaxis_title=plt_kwargs.pop('xlabel', 'Time (s)'),
                      yaxis_title=plt_kwargs.pop('ylabel', 'Voltage'))
    fig.show()


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
    """

    fig = px.histogram(x=isis, nbins=bins, range_x=range, histnorm='probability' if density else None)

    # Update layout
    fig.update_layout(title=plt_kwargs.pop('title', 'ISIs'),
                      xaxis_title=plt_kwargs.pop('xlabel', 'Time'),
                      yaxis_title='Density' if density else 'Count')
    fig.show()


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

    labels = ['U' + str(ind) for ind in range(len(rates))]
    fig = px.bar(x=labels, y=rates)

    # Update layout
    fig.update_layout(title=plt_kwargs.pop('title', 'Firing Rates of all Units'),
                      xaxis_title=plt_kwargs.pop('xlabel', 'Units'),
                      yaxis_title=plt_kwargs.pop('ylabel', 'Firing Rate (Hz)'))
    fig.show()
```