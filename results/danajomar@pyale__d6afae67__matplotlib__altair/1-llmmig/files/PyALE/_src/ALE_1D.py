import numpy as np
import pandas as pd
import altair as alt

from .lib import quantile_ied, CI_estimate, order_groups


def plot_1D_continuous_eff(res_df, X):
    """Plot the 1D ALE plot for a continuous feature using Altair.

    Arguments:
    res_df -- A pandas DataFrame containing the computed effects
    (the output of ale_1D_continuous).
    X -- The dataset used to compute the effects.
    """

    feature_name = res_df.index.name
    res_df = res_df.reset_index()

    # Create a rug plot for the distribution of the feature
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
    rug_df = pd.DataFrame({feature_name: rug})

    # Base line plot for the effect
    base = alt.Chart(res_df).mark_line().encode(
        x=alt.X(feature_name, title=feature_name),
        y=alt.Y("eff", title="Effect on prediction (centered)"),
    )

    # Rug plot
    rug_plot = alt.Chart(rug_df).mark_tick(opacity=0.2, color="black").encode(
        x=alt.X(feature_name, title=None),
        y=alt.value(0),  # Place rug ticks at the bottom
    )

    # Confidence interval
    lowerCI_name = res_df.columns[res_df.columns.str.contains("lowerCI")]
    upperCI_name = res_df.columns[res_df.columns.str.contains("upperCI")]
    if (len(lowerCI_name) == 1) and (len(upperCI_name) == 1):
        ci_band = alt.Chart(res_df).mark_area(opacity=0.2, color="grey").encode(
            x=alt.X(feature_name, title=feature_name),
            y=alt.Y(lowerCI_name[0], title=""),
            y2=alt.Y2(upperCI_name[0]),
        )
        chart = ci_band + base + rug_plot
    else:
        chart = base + rug_plot

    chart = chart.properties(
        title="1D ALE Plot - Continuous",
        width=800,
        height=400,
    )
    return chart


def plot_1D_discrete_eff(res_df, X):
    """Plot the 1D ALE plot for a discrete feature using Altair.

    Arguments:
    res_df -- A pandas DataFrame with the computed effects
    (the output of ale_1D_discrete).
    X -- The dataset used to compute the effects.
    """

    feature_name = res_df.index.name
    res_df = res_df.reset_index()

    # Error bars for confidence intervals
    lowerCI_name = res_df.columns[res_df.columns.str.contains("lowerCI")]
    upperCI_name = res_df.columns[res_df.columns.str.contains("upperCI")]
    if (len(lowerCI_name) == 1) and (len(upperCI_name) == 1):
        res_df["yerr_lower"] = res_df["eff"] - res_df[lowerCI_name[0]]
        res_df["yerr_upper"] = res_df[upperCI_name[0]] - res_df["eff"]
        error_bars = alt.Chart(res_df).mark_errorbar().encode(
            x=alt.X(feature_name, title=feature_name),
            y=alt.Y("eff", title="Effect on prediction (centered)"),
            yErrorMinus="yerr_lower",
            yErrorPlus="yerr_upper",
        )
    else:
        error_bars = alt.Chart()

    # Line and point plot for effects
    points = alt.Chart(res_df).mark_line(point=True).encode(
        x=alt.X(feature_name, title=feature_name),
        y=alt.Y("eff", title="Effect on prediction (centered)"),
    )

    # Bar chart for sizes
    bars = alt.Chart(res_df).mark_bar(opacity=0.1, color="lightblue").encode(
        x=alt.X(feature_name, title=feature_name),
        y=alt.Y("size", title="Size"),
    )

    chart = alt.layer(bars, points, error_bars).resolve_scale(y="independent").properties(
        title="1D ALE Plot - Discrete/Categorical",
        width=800,
        height=400,
    )
    return chart
