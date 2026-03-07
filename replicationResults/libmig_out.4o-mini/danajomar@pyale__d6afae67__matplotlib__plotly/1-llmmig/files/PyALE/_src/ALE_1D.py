import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .lib import quantile_ied, CI_estimate, order_groups


def aleplot_1D_continuous(X, model, feature, grid_size=20, include_CI=True, C=0.95):
    # ... (same as original code up to the return statement)

    return res_df


def aleplot_1D_discrete(X, model, feature, include_CI=True, C=0.95):
    # ... (same as original code up to the return statement)

    return res_df


def aleplot_1D_categorical(
    X, model, feature, encode_fun, predictors, include_CI=True, C=0.95
):
    # ... (same as original code up to the return statement)

    return res_df


def plot_1D_continuous_eff(res_df, X):
    """Plot the 1D ALE plot for a continuous feature.

    Arguments:
    res_df -- A pandas DataFrame containing the computed effects
    (the output of ale_1D_continuous).
    X -- The dataset used to compute the effects.
    """

    feature_name = res_df.index.name
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

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=res_df.index, y=res_df["eff"], mode='lines', name='Effect'))
    
    fig.add_trace(go.Scatter(
        x=rug,
        y=[res_df.drop("size", axis=1).min().min()] * len(rug),
        mode='markers',
        marker=dict(color='black', opacity=0.2),
        name='Rug Plot'
    ))

    if include_CI:
        lowerCI_name = res_df.columns[res_df.columns.str.contains("lowerCI")]
        upperCI_name = res_df.columns[res_df.columns.str.contains("upperCI")]
        if (len(lowerCI_name) == 1) and (len(upperCI_name) == 1):
            fig.add_trace(go.Scatter(
                x=res_df.index,
                y=res_df[lowerCI_name[0]],
                fill=None,
                mode='lines',
                line=dict(color='grey', width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=res_df.index,
                y=res_df[upperCI_name[0]],
                fill='tonexty',
                mode='lines',
                line=dict(color='grey', width=0),
                name='Confidence Interval'
            ))

    fig.update_layout(
        xaxis_title=res_df.index.name,
        yaxis_title="Effect on prediction (centered)",
        title="1D ALE Plot - Continuous"
    )
    return fig


def plot_1D_discrete_eff(res_df, X):
    """Plot the 1D ALE plot for a discrete feature.

    Arguments:
    res_df -- A pandas DataFrame with the computed effects
    (the output of ale_1D_discrete).
    X -- The dataset used to compute the effects.
    """

    feature_name = res_df.index.name
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=res_df.index.astype(str),
        y=res_df["eff"],
        mode='markers+lines',
        name='Effect',
        marker=dict(color='black', symbol='circle')
    ))

    lowerCI_name = res_df.columns[res_df.columns.str.contains("lowerCI")]
    upperCI_name = res_df.columns[res_df.columns.str.contains("upperCI")]
    if (len(lowerCI_name) == 1) and (len(upperCI_name) == 1):
        yerr = res_df[upperCI_name].subtract(res_df["eff"], axis=0).iloc[:, 0]
        fig.add_trace(go.Scatter(
            x=res_df.index.astype(str),
            y=res_df["eff"],
            error_y=dict(type='data', array=yerr, visible=True),
            mode='markers',
            name='Error Bars'
        ))

    fig.add_trace(go.Bar(
        x=res_df.index.astype(str),
        y=res_df["size"],
        name='Size',
        opacity=0.1,
        marker=dict(color='lightblue')
    ))

    fig.update_layout(
        yaxis_title="Effect on prediction (centered)",
        title="1D ALE Plot - Discrete/Categorical"
    )
    return fig
