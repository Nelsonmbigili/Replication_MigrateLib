### Explanation of Changes

To migrate the provided code from using `matplotlib` to `plotly`, several key changes were made:

1. **Import Statements**: The import statements were updated to include `plotly.graph_objects` instead of `matplotlib.pyplot`.
2. **Plotting Functions**: The plotting functions were replaced with their `plotly` equivalents. For example, `ax.plot` was replaced with `go.Scatter`, and `ax.fill_between` was replaced with `go.Scatter` for shaded areas.
3. **3D Plotting**: The 3D plotting was changed from `ax.plot` to `go.Scatter3d`.
4. **Heatmap**: The 2D histogram was replaced with `go.Histogram2d`.
5. **Layout and Figure Creation**: The way figures and layouts are created and displayed in `plotly` differs from `matplotlib`, so adjustments were made to accommodate this.
6. **Axis Configuration**: The configuration of axes and titles was adapted to fit the `plotly` syntax.

The overall structure of the functions remains the same, but the plotting logic is now compatible with `plotly`.

### Modified Code

```python
"""Plots for spikes."""

import numpy as np
import plotly.graph_objects as go

from spiketools.utils.options import get_avg_func, get_var_func
from spiketools.plts.data import plot_bar, plot_hist, plot_lines
from spiketools.plts.utils import check_ax, get_kwargs, savefig
from spiketools.plts.style import set_plt_kwargs

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_waveform(waveform, timestamps=None, average=None, shade=None, add_traces=False,
                  ax=None, **plt_kwargs):
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
    ax : Axes, optional
        Axis object upon which to plot.
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

    fig.add_trace(go.Scatter(x=timestamps, y=waveform, mode='lines',
                             name='Average Waveform',
                             line=dict(width=2)))

    if add_traces:
        for i in range(all_waveforms.shape[0]):
            fig.add_trace(go.Scatter(x=timestamps, y=all_waveforms[i], mode='lines',
                                     name=f'Trace {i+1}',
                                     line=dict(width=custom_plt_kwargs.pop('traces_lw', 1),
                                               opacity=custom_plt_kwargs.pop('traces_alpha', 0.5),
                                               color='rgba(0,0,0,0.5)')))

    if shade is not None:
        fig.add_trace(go.Scatter(x=np.concatenate([timestamps, timestamps[::-1]]),
                                  y=np.concatenate([waveform - shade, (waveform + shade)[::-1]]),
                                  fill='toself', fillcolor='rgba(0,100,80,0.2)',
                                  line=dict(color='rgba(255,255,255,0)'),
                                  name='Shade'))

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

    fig = go.Figure()

    if timestamps is None:
        timestamps = np.arange(waveforms.shape[-1])

    for ind, waveform in enumerate(waveforms):
        fig.add_trace(go.Scatter3d(x=timestamps, y=np.ones(waveform.shape[0]) * ind, z=waveform,
                                     mode='lines', name=f'Waveform {ind}'))

    fig.update_layout(title=plt_kwargs.pop('title', 'Spike Waveforms'),
                      scene=dict(xaxis_title='Time',
                                 yaxis_title='Waveform Index',
                                 zaxis_title='Voltage'))

    fig.show()


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
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    xlabel = 'Time (s)'
    if timestamps is None:
        timestamps = np.arange(waveforms.shape[-1])
        xlabel = 'Samples'
    timestamps = np.vstack([timestamps] * waveforms.shape[0])

    fig = go.Figure(data=go.Histogram2d(x=timestamps.flatten(), y=waveforms.flatten(),
                                          colorscale=cmap, nbinsx=bins[0], nbinsy=bins[1]))

    fig.update_layout(title=plt_kwargs.pop('title', 'Spike Histogram'),
                      xaxis_title=plt_kwargs.pop('xlabel', xlabel),
                      yaxis_title=plt_kwargs.pop('ylabel', 'Voltage'))

    fig.show()


@savefig
@set_plt_kwargs
def plot_isis(isis, bins=None, range=None, density=False, ax=None, **plt_kwargs):
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
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    plot_hist(isis, bins, range, density, ax=ax,
              xlabel=plt_kwargs.pop('xlabel', 'Time'),
              title=plt_kwargs.pop('title', 'ISIs'),
              **plt_kwargs)


@savefig
@set_plt_kwargs
def plot_firing_rates(rates, ax=None, **plt_kwargs):
    """Plot firing rates for a group of neurons.

    Parameters
    ----------
    rates : list of float
        Firing rates.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    plot_bar(rates, labels=['U' + str(ind) for ind in range(len(rates))], ax=ax,
             xlabel=plt_kwargs.pop('xlabel', 'Units'),
             ylabel=plt_kwargs.pop('xlabel', 'Firing Rate (Hz)'),
             title=plt_kwargs.pop('title', 'Firing Rates of all Units'),
             **plt_kwargs)
```