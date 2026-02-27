"""Plotting tools for Gammy models and formulae using Altair"""

import logging
from typing import Callable, List, Optional, Union

import bayespy as bp
import altair as alt
import pandas as pd
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
    """Validation plot for a GAM object using Altair"""

    N = len(model.formula)
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

    time_series_data = pd.DataFrame({
        "Index": index,
        "Observations": y,
        "Predictions": mu,
        "Lower Bound": lower,
        "Upper Bound": upper
    })

    time_series_chart = alt.Chart(time_series_data).mark_line().encode(
        x="Index",
        y="Predictions",
        color=alt.value("black")
    ).properties(title="Time Series Plot")

    scatter_chart = alt.Chart(time_series_data).mark_point(opacity=0.3).encode(
        x="Index",
        y="Observations",
        color=alt.value(color)
    )

    time_series_chart = time_series_chart + scatter_chart

    # XY-plot
    xy_data = pd.DataFrame({
        "Predictions": mu,
        "Observations": y
    })

    xy_chart = alt.Chart(xy_data).mark_point(opacity=0.3).encode(
        x="Predictions",
        y="Observations",
        color=alt.value(color)
    ).properties(title="Predictions vs Observations")

    # Partial residual plots
    partial_residual_charts = []
    for i, ((mu, sigma), res, input_map, xlabel, title) in enumerate(
        zip(marginals, residuals, input_maps, xlabels, titles)
    ):
        x = input_map(grid)
        if len(x.shape) == 1 or x.shape[1] == 1:
            lower = mu - 2 * np.sqrt(sigma)
            upper = mu + 2 * np.sqrt(sigma)

            partial_data = pd.DataFrame({
                "Input": input_map(input_data),
                "Residuals": res,
                "Grid": x,
                "Mean": mu,
                "Lower Bound": lower,
                "Upper Bound": upper
            })

            scatter = alt.Chart(partial_data).mark_point(opacity=0.3).encode(
                x="Input",
                y="Residuals",
                color=alt.value(color)
            )

            line = alt.Chart(partial_data).mark_line(color="black").encode(
                x="Grid",
                y="Mean"
            )

            band = alt.Chart(partial_data).mark_area(opacity=0.3).encode(
                x="Grid",
                y="Lower Bound",
                y2="Upper Bound"
            )

            partial_chart = (scatter + line + band).properties(title=title)
            partial_residual_charts.append(partial_chart)

    return [time_series_chart, xy_chart] + partial_residual_charts


def gaussian1d_density_plot(model: gammy.bayespy.GAM):
    """Plot 1-D density for each parameter using Altair"""

    N = len(model.formula)
    density_charts = []

    # Plot inverse gamma
    (b, a) = (-model.tau.phi[0], model.tau.phi[1])
    mu = a / b
    grid = np.arange(0.5 * mu, 1.5 * mu, mu / 300)
    tau_data = pd.DataFrame({
        "Grid": grid,
        "Density": model.tau.pdf(grid)
    })

    tau_chart = alt.Chart(tau_data).mark_line().encode(
        x="Grid",
        y="Density"
    ).properties(title=r"$\tau$ = noise inverse variance")

    density_charts.append(tau_chart)

    # Plot marginal thetas
    for i, theta in enumerate(model.theta_marginals):
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

        theta_data = pd.DataFrame({
            "Grid": grid,
            "Density": [bp.nodes.GaussianARD(mu, 1 / std ** 2).pdf(grid)
                        for (mu, std) in zip(mus, stds)]
        })

        theta_chart = alt.Chart(theta_data).mark_line().encode(
            x="Grid",
            y="Density"
        ).properties(title=r"$\theta_{0}$".format(i))

        density_charts.append(theta_chart)

    return density_charts
