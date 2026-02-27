import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .lib import quantile_ied, CI_estimate, order_groups


def plot_1D_continuous_eff(res_df, X):
    """Plot the 1D ALE plot for a continuous feature using Plotly.

    Arguments:
    res_df -- A pandas DataFrame containing the computed effects
    (the output of ale_1D_continuous).
    X -- The dataset used to compute the effects.
    """

    feature_name = res_df.index.name
    # position: jitter
    sorted_values = X[feature_name].sort_values()
    values_diff = abs(sorted_values.shift() - sorted_values)
    np.random.seed(123)
    rug = X.apply(
        lambda row: row[feature_name]
        + np.random.uniform(
            -values_diff[values_diff > 0].min() / 2,
            values_diff[values_diff > 0].min() / 2,
        ),
        axis=1,
    )

    # Create the main effect line
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=res_df.index,
            y=res_df["eff"],
            mode="lines",
            name="Effect",
            line=dict(color="blue"),
        )
    )

    # Add rug plot
    fig.add_trace(
        go.Scatter(
            x=rug,
            y=[res_df.drop("size", axis=1).min().min()] * len(rug),
            mode="markers",
            marker=dict(symbol="line-ns", color="black", opacity=0.2),
            name="Rug",
        )
    )

    # Add confidence intervals if available
    lowerCI_name = res_df.columns[res_df.columns.str.contains("lowerCI")]
    upperCI_name = res_df.columns[res_df.columns.str.contains("upperCI")]
    if (len(lowerCI_name) == 1) and (len(upperCI_name) == 1):
        fig.add_trace(
            go.Scatter(
                x=res_df.index,
                y=res_df[lowerCI_name[0]],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=res_df.index,
                y=res_df[upperCI_name[0]],
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(128, 128, 128, 0.2)",
                line=dict(width=0),
                name=f"{lowerCI_name.str.split('_')[0][1]}% Confidence Interval",
            )
        )

    # Update layout
    fig.update_layout(
        title="1D ALE Plot - Continuous",
        xaxis_title=feature_name,
        yaxis_title="Effect on prediction (centered)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_1D_discrete_eff(res_df, X):
    """Plot the 1D ALE plot for a discrete feature using Plotly.

    Arguments:
    res_df -- A pandas DataFrame with the computed effects
    (the output of ale_1D_discrete).
    X -- The dataset used to compute the effects.
    """

    feature_name = res_df.index.name

    # Create the main effect line with error bars
    lowerCI_name = res_df.columns[res_df.columns.str.contains("lowerCI")]
    upperCI_name = res_df.columns[res_df.columns.str.contains("upperCI")]
    yerr = None
    if (len(lowerCI_name) == 1) and (len(upperCI_name) == 1):
        yerr = res_df[upperCI_name].subtract(res_df["eff"], axis=0).iloc[:, 0]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=res_df.index.astype(str),
            y=res_df["eff"],
            mode="lines+markers",
            error_y=dict(
                type="data",
                array=yerr,
                visible=True,
                color="black",
                thickness=1.5,
                width=3,
            )
            if yerr is not None
            else None,
            name="Effect",
            line=dict(color="black", dash="dash"),
            marker=dict(symbol="circle", size=8),
        )
    )

    # Add bar chart for sizes
    fig.add_trace(
        go.Bar(
            x=res_df.index.astype(str),
            y=res_df["size"],
            name="Size",
            marker=dict(color="lightblue", opacity=0.5),
            yaxis="y2",
        )
    )

    # Update layout
    fig.update_layout(
        title="1D ALE Plot - Discrete/Categorical",
        xaxis_title=feature_name,
        yaxis_title="Effect on prediction (centered)",
        yaxis2=dict(
            title="Size",
            overlaying="y",
            side="right",
            showgrid=False,
            titlefont=dict(color="lightblue"),
            tickfont=dict(color="lightblue"),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="overlay",
    )
    return fig
