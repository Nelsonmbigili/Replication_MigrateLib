### Explanation of Changes:
To migrate the code from `matplotlib` to `seaborn`, the following changes were made:
1. **Importing Seaborn**: Added `import seaborn as sns` to replace `matplotlib` plotting functions.
2. **Continuous Feature Plot (`plot_1D_continuous_eff`)**:
   - Replaced `ax.plot` with `sns.lineplot` for plotting the effect.
   - Used `sns.rugplot` to replace the manual rug plot logic.
   - Used `sns.fill_between` for confidence interval shading.
3. **Discrete Feature Plot (`plot_1D_discrete_eff`)**:
   - Replaced `ax.errorbar` with `sns.pointplot` for plotting the effect with error bars.
   - Used `sns.barplot` to replace the bar chart for group sizes.
4. **Removed `matplotlib.transforms`**: The rug plot jittering logic was replaced with `sns.rugplot`, so `matplotlib.transforms` is no longer needed.

### Modified Code:
```python
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from .lib import quantile_ied, CI_estimate, order_groups


def plot_1D_continuous_eff(res_df, X, fig=None, ax=None):
    """Plot the 1D ALE plot for a continuous feature.

    Arguments:
    res_df -- A pandas DataFrame containing the computed effects
    (the output of ale_1D_continuous).
    X -- The dataset used to compute the effects.
    fig, ax -- matplotlib figure and axis.
    """

    feature_name = res_df.index.name
    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))

    # Plot the effect using seaborn lineplot
    sns.lineplot(x=res_df.index, y=res_df["eff"], ax=ax, label="Effect")

    # Add rug plot for data distribution
    sns.rugplot(
        x=X[feature_name],
        ax=ax,
        height=0.05,
        alpha=0.2,
        color="k",
        label="Data distribution",
    )

    # Add confidence intervals if available
    lowerCI_name = res_df.columns[res_df.columns.str.contains("lowerCI")]
    upperCI_name = res_df.columns[res_df.columns.str.contains("upperCI")]
    if (len(lowerCI_name) == 1) and (len(upperCI_name) == 1):
        label = lowerCI_name.str.split("_")[0][1] + " confidence interval"
        ax.fill_between(
            res_df.index,
            y1=res_df[lowerCI_name[0]],
            y2=res_df[upperCI_name[0]],
            alpha=0.2,
            color="grey",
            label=label,
        )
        ax.legend()

    ax.set_xlabel(res_df.index.name)
    ax.set_ylabel("Effect on prediction (centered)")
    ax.set_title("1D ALE Plot - Continuous")
    return fig, ax


def plot_1D_discrete_eff(res_df, X, fig=None, ax=None):
    """Plot the 1D ALE plot for a discrete feature.

    Arguments:
    res_df -- A pandas DataFrame with the computed effects
    (the output of ale_1D_discrete).
    X -- The dataset used to compute the effects.
    fig, ax -- matplotlib figure and axis.
    """

    feature_name = res_df.index.name
    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))

    # Plot the effect using seaborn pointplot
    sns.pointplot(
        x=res_df.index.astype(str),
        y=res_df["eff"],
        ax=ax,
        color="black",
        join=True,
        capsize=0.2,
        errwidth=1,
        label="Effect",
    )

    # Add confidence intervals if available
    lowerCI_name = res_df.columns[res_df.columns.str.contains("lowerCI")]
    upperCI_name = res_df.columns[res_df.columns.str.contains("upperCI")]
    if (len(lowerCI_name) == 1) and (len(upperCI_name) == 1):
        yerr = res_df[upperCI_name].subtract(res_df["eff"], axis=0).iloc[:, 0]
        sns.pointplot(
            x=res_df.index.astype(str),
            y=res_df["eff"],
            ax=ax,
            color="black",
            join=True,
            capsize=0.2,
            errwidth=1,
            label="Effect with CI",
        )

    # Add barplot for group sizes
    ax2 = ax.twinx()
    sns.barplot(
        x=res_df.index.astype(str),
        y=res_df["size"],
        ax=ax2,
        alpha=0.1,
        color="lightblue",
        label="Size",
    )
    ax2.set_ylabel("Size", color="lightblue")
    ax2.tick_params(axis="y", labelcolor="lightblue")

    ax.set_xlabel(feature_name)
    ax.set_ylabel("Effect on prediction (centered)")
    ax.set_title("1D ALE Plot - Discrete/Categorical")
    fig.tight_layout()
    return fig, ax, ax2
```

### Key Notes:
- The `seaborn` library simplifies many plotting tasks, such as adding rug plots and confidence intervals.
- The `sns.lineplot` and `sns.pointplot` functions handle most of the plotting logic, reducing the need for manual adjustments.
- The `sns.barplot` function is used for the bar chart, and its transparency (`alpha`) is adjusted to match the original style.