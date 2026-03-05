"""Plotting tools for Gammy models and formulae

"""

import logging
from typing import Callable, List, Optional, Union

import bayespy as bp
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

import gammy
from gammy import utils
from gammy.utils import pipe


def validation_plot(
        model,
        input_data,
        y,
        grid_limits,
        input_maps,
        index=None,
        xlabels=None,
        titles=None,
        gridsize=20,
        color="red",
        **kwargs
):
    """Validation plot for a GAM object

    Contains:

        - Series plot with predicted vs. observed
        - Partial residual plots

    Parameters
    ----------
    model : gammy.bayespy.GAM | gammy.numpy.GAM
        Visualized model
    input_data : np.ndarray
        Input data
    y : np.ndarray
        Observations
    grid_limits : List
        Grid limits, either `[a, b]` or `[[a_1, b_1], ..., [a_N, b_N]]`
    input_maps : List[Callable]
        List of input maps to be used for each pair of grid limits
    index : np.ndarray
        Optional x-axis for the series plot
    xlabels : List[str]
        Optional x-labels for the partial residual plots
    gridsize : int
        Number of points in the input dimensions discretizations
    color : str
        Color of scatter points

    """

    N = len(model.formula)
    N_rows = 2 + (N + 1) // 2
    fig = make_subplots(rows=N_rows, cols=2)

    xlabels = xlabels or [None] * len(model.formula)
    titles = titles or [None] * len(model.formula)
    index = np.arange(len(input_data)) if index is None else index

    assert (
        len(grid_limits) == 2 if len(input_data.shape) == 1 else
        (
            len(grid_limits) == input_data.shape[1] and
            all([len(xs) == 2 for xs in grid_limits])
        )
    ), (
        "Given grid limits do not match with the shape of input data."
    )
    assert len(model.formula.terms) == len(input_maps), (
        "Must give exactly one input per model term."
    )
    assert len(model.formula.terms) == len(titles), (
        "Must give exactly one title per model term."
    )

    # Data and predictions
    grid = np.array(
        utils.listmap(lambda x: np.linspace(x[0], x[1], gridsize))(grid_limits)
    ).T if len(input_data.shape) == 2 else np.linspace(
        grid_limits[0], grid_limits[1], gridsize
    )
    marginals = model.predict_variance_marginals(grid)
    residuals = model.marginal_residuals(input_data, y)

    # Time series plot
    (mu, sigma_theta) = model.predict_variance_theta(input_data)
    lower = mu - 2 * np.sqrt(sigma_theta + model.inv_mean_tau)
    upper = mu + 2 * np.sqrt(sigma_theta + model.inv_mean_tau)
    fig.add_trace(go.Scatter(x=index, y=y, mode='markers', marker=dict(color=color, opacity=0.3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=index, y=mu, mode='lines', line=dict(color='black')), row=1, col=1)
    fig.add_trace(go.Scatter(x=index, y=lower, mode='lines', line=dict(color='black', width=0), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=index, y=upper, mode='lines', fill='tonexty', fillcolor='rgba(0,0,0,0.3)', line=dict(color='black', width=0), showlegend=False), row=1, col=1)

    # XY-plot
    fig.add_trace(go.Scatter(x=mu, y=y, mode='markers', marker=dict(color=color, opacity=0.3)), row=2, col=1)
    fig.add_trace(go.Scatter(x=[mu.min(), mu.max()], y=[mu.min(), mu.max()], mode='lines', line=dict(color='black'), name='x=y'), row=2, col=1)
    fig.update_xaxes(title_text="Predictions", row=2, col=1)
    fig.update_yaxes(title_text="Observations", row=2, col=1)

    # Partial residual plots
    for i, ((mu, sigma), res, input_map, xlabel, title) in enumerate(
        zip(marginals, residuals, input_maps, xlabels, titles)
    ):
        x = input_map(grid)
        if len(x.shape) == 1 or x.shape[1] == 1:
            (lower, upper) = (
                mu - 2 * np.sqrt(sigma),
                mu + 2 * np.sqrt(sigma)
            )
            fig.add_trace(go.Scatter(x=input_map(input_data), y=res, mode='markers', marker=dict(color=color), **kwargs), row=2 + i // 2, col=i % 2 + 1)
            fig.add_trace(go.Scatter(x=x, y=mu, mode='lines', line=dict(color='black', width=2)), row=2 + i // 2, col=i % 2 + 1)
            fig.add_trace(go.Scatter(x=x, y=lower, mode='lines', line=dict(color='black', width=0), showlegend=False), row=2 + i // 2, col=i % 2 + 1)
            fig.add_trace(go.Scatter(x=x, y=upper, mode='lines', fill='tonexty', fillcolor='rgba(0,0,0,0.3)', line=dict(color='black', width=0), showlegend=False), row=2 + i // 2, col=i % 2 + 1)
            fig.update_xaxes(title_text=xlabel, row=2 + i // 2, col=i % 2 + 1)
        elif x.shape[1] == 2:
            u, v = np.meshgrid(x[:, 0], x[:, 1])
            w = np.hstack((
                u.reshape(-1, 1), v.reshape(-1, 1)
            ))
            # Override mu and sigma on purpose!
            (mu, sigma) = model.predict_variance_marginal(w, i)
            mu_mesh = mu.reshape(u.shape)
            fig.add_trace(go.Surface(z=mu_mesh, x=u, y=v), row=2 + i // 2, col=i % 2 + 1)
        else:
            raise NotImplementedError("High-dimensional plots not supported.")
        fig.update_layout(title=title)

    fig.update_layout(height=600, width=800)
    return fig


def gaussian1d_density_plot(model: gammy.bayespy.GAM):
    """Plot 1-D density for each parameter

    """
    N = len(model.formula)
    N_rows = 2 + (N + 1) // 2
    fig = make_subplots(rows=N + 1, cols=1)

    # Plot inverse gamma
    (b, a) = (-model.tau.phi[0], model.tau.phi[1])
    mu = a / b
    grid = np.arange(0.5 * mu, 1.5 * mu, mu / 300)
    fig.add_trace(go.Scatter(x=grid, y=model.tau.pdf(grid), mode='lines'), row=1, col=1)
    fig.update_layout(title=r"$\tau$ = noise inverse variance")

    # Plot marginal thetas
    for i, theta in enumerate(model.theta_marginals):
        ax = fig.add_subplot(gs[i + 1])
        mus = theta.get_moments()[0]
        mus = np.array([mus]) if mus.shape == () else mus
        cov = utils.solve_covariance(theta.get_moments())
        stds = pipe(
            np.array([cov]) if cov.shape == ()
            else np.diag(cov),
            np.sqrt
        )
        left = (mus - 4 * stds).min()
        right = (mus + 4 * stds).max()
        grid = np.arange(left, right, (right - left) / 300)
        for (mu, std) in zip(mus, stds):
            node = bp.nodes.GaussianARD(mu, 1 / std ** 2)
            fig.add_trace(go.Scatter(x=grid, y=node.pdf(grid), mode='lines'), row=i + 2, col=1)
        fig.update_layout(title=r"$\theta_{0}$".format(i))

    fig.update_layout(height=600, width=800)
    return fig


def gaussian2d_density_plot(model: gammy.bayespy.GAM, i, j):
    """Plot 2-D joint distribution of indices i and j

    """
    raise NotImplementedError


def covariance_plot(model, ax=None, linthresh=0.1, **kwargs):
    """Covariance matrix

    """

    fig = go.Figure()
    C = model.covariance_theta
    fig.add_trace(go.Heatmap(z=C, colorscale='Viridis', **kwargs))

    return fig


def basis_plot(
        formula: gammy.formulae.Formula,
        grid_limits,
        input_maps,
        gridsize=20
):
    """Plot all basis functions

    """
    # Figure definition
    N = len(formula)
    fig = make_subplots(rows=N, cols=1)

    # Data and predictions
    grid = (
        pipe(
            grid_limits,
            utils.listmap(lambda x: np.linspace(x[0], x[1], gridsize)),
            lambda x: np.array(x).T
        )
    )

    # Plot stuff
    for i, (basis, input_map) in enumerate(zip(formula.terms, input_maps)):
        x = input_map(grid)
        for f in basis:
            fig.add_trace(go.Scatter(x=x, y=f(grid), mode='lines'), row=i + 1, col=1)

    return fig
