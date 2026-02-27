"""Plots for different data types / layouts."""

from itertools import repeat

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt  # Retained for polar plots and text annotations

from spiketools.measures.circular import bin_circular
from spiketools.utils.options import get_avg_func
from spiketools.plts.annotate import add_vlines, add_text_labels
from spiketools.plts.utils import check_ax, savefig
from spiketools.plts.style import set_plt_kwargs
from spiketools.plts.settings import TEXT_SETTINGS

###################################################################################################
###################################################################################################

@savefig
@set_plt_kwargs
def plot_lines(x_values, y_values, vline=None, ax=None, **plt_kwargs):
    """Plot data as a line."""

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    x_values = repeat(x_values) if (isinstance(x_values, np.ndarray) and x_values.ndim == 1) \
        else x_values
    y_values = [y_values] if (isinstance(y_values, np.ndarray) and y_values.ndim == 1) \
        else y_values

    for x_vals, y_vals in zip(x_values, y_values):
        sns.lineplot(x=x_vals, y=y_vals, ax=ax, **plt_kwargs)

    add_vlines(vline, ax)


@savefig
@set_plt_kwargs
def plot_scatter(x_values, y_values, ax=None, **plt_kwargs):
    """Plot 2d data as a scatter plot."""

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    sns.scatterplot(x=x_values, y=y_values, ax=ax, **plt_kwargs)


@savefig
@set_plt_kwargs
def plot_points(data, label=None, ax=None, **plt_kwargs):
    """Plot 1d data as points."""

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', (2.5, 5)))

    n_points = len(data)
    xs = np.zeros(n_points) + 0.1 * np.random.rand(n_points)

    sns.scatterplot(x=xs, y=data, ax=ax,
                    s=plt_kwargs.pop('ms', 20)**2,  # Seaborn uses `s` for marker size
                    alpha=plt_kwargs.pop('alpha', 0.5),
                    **plt_kwargs)

    ax.set_xlim([-0.25, 0.25])
    ax.set_xticks([])
    if label:
        ax.set(xticks=[0], xticklabels=[label])


@savefig
@set_plt_kwargs
def plot_hist(data, bins=None, range=None, density=None,
              average=None, ax=None, **plt_kwargs):
    """Plot data as a histogram."""
    """Plot data as a histogram.

    Parameters
    ----------
    data : 1d array
        Data to plot.
    bins : int or list, optional
        Bin definition, either a number of bins to use, or bin definitions.
    range : tuple, optional
        Range of the data to plot.
    density : bool, optional, default: False
        Whether to draw a probability density.
    average : {'median', 'mean'}, optional
        Which kind of average to compute and add to the plot.
        If None, no average is plotted.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    sns.histplot(data, bins=bins, binrange=range, stat='density' if density else 'count', ax=ax, **plt_kwargs)

    if average:
        add_vlines(get_avg_func(average)(data), lw=4, color='red', alpha=0.8, ax=ax)


@savefig
@set_plt_kwargs
def plot_bar(data, labels=None, add_text=False, ax=None, **plt_kwargs):
    """Plot data in a bar graph."""

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if not labels:
        labels = ['d' + str(ind) for ind in range(len(data))]

    sns.barplot(x=labels, y=data, ax=ax, **plt_kwargs)
    ax.set(xlim=[-0.5, len(data)-0.5])

    if add_text:
        add_text_labels(data, axis='x', location=data, colors='white')


@savefig
@set_plt_kwargs
def plot_barh(data, labels=None, add_text=False, ax=None, **plt_kwargs):
    """Plot a horizontal bar plot."""

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    if not labels:
        labels = ['d' + str(ind) for ind in range(len(data))]

    sns.barplot(x=data, y=labels, ax=ax, **plt_kwargs)

    if add_text:
        add_text_labels(data, axis='y', location=data, colors='white')


@savefig
@set_plt_kwargs
def plot_polar_hist(data, bin_width=10, ax=None, **plt_kwargs):
    """Plot a polar histogram."""

    if not ax:
        ax = plt.subplot(111, polar=True)

    bin_edges, counts = bin_circular(data, bin_width=bin_width)
    ax.bar(bin_edges[:-1], counts, **plt_kwargs)


@savefig
@set_plt_kwargs
def plot_text(text, xpos=0.5, ypos=0.5, show_axis=False, ax=None, **plt_kwargs):
    """Plot text."""

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', None))

    ax.text(xpos, ypos, text,
            fontdict=plt_kwargs.pop('fontdict', TEXT_SETTINGS['fontdict']),
            ha=plt_kwargs.pop('ha', TEXT_SETTINGS['ha']),
            va=plt_kwargs.pop('va', TEXT_SETTINGS['va']),
            **plt_kwargs)

    if not show_axis:
        ax.axis('off')