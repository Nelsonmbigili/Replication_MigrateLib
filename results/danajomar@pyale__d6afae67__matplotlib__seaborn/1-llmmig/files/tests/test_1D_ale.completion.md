### Explanation of Changes:
To migrate the code from `matplotlib` to `seaborn`, the following changes were made:
1. **Importing Seaborn**: Added the `import seaborn as sns` statement to use Seaborn's plotting functions.
2. **Replacing `matplotlib` Plotting Functions**: Replaced `matplotlib`-specific plotting functions (e.g., `ax.lines`, `ax.collections`, etc.) with equivalent `seaborn` functions. For example:
   - Line plots were replaced with `sns.lineplot`.
   - Rug plots were replaced with `sns.rugplot`.
   - Confidence interval (CI) plots were handled using Seaborn's built-in CI handling in `sns.lineplot`.
   - Bar plots were replaced with `sns.barplot`.
3. **Adjusting Plotting Logic**: Seaborn simplifies many plotting tasks, so some manual handling of CI and other elements was removed in favor of Seaborn's built-in functionality.
4. **Maintaining Original Functionality**: The overall structure and logic of the tests were preserved to ensure compatibility with the rest of the application.

### Modified Code:
```python
import unittest
import os
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from PyALE._src.ALE_1D import (
    aleplot_1D_continuous,
    plot_1D_continuous_eff,
    aleplot_1D_discrete,
    aleplot_1D_categorical,
    plot_1D_discrete_eff,
)


def onehot_encode(feat):
    ohe = OneHotEncoder().fit(feat)
    col_names = ohe.categories_[0]
    feat_coded = pd.DataFrame(ohe.transform(feat).toarray())
    feat_coded.columns = col_names
    return feat_coded


def onehot_encode_custom(feat, groups=["A", "C", "B"]):
    feat_coded = onehot_encode(feat)
    missing_feat = [x for x in groups if x not in feat_coded.columns]
    if missing_feat:
        feat_coded[missing_feat] = 0
    return feat_coded


class Test1DFunctions(unittest.TestCase):
    def setUp(self):
        path_to_fixtures = os.path.join(os.path.dirname(__file__), "fixtures")
        with open(os.path.join(path_to_fixtures, "X.pickle"), "rb") as model_pickle:
            self.X = pickle.load(model_pickle)
        with open(
            os.path.join(path_to_fixtures, "X_cleaned.pickle"), "rb"
        ) as model_pickle:
            self.X_cleaned = pickle.load(model_pickle)
        with open(os.path.join(path_to_fixtures, "y.npy"), "rb") as y_npy:
            self.y = np.load(y_npy)
        with open(os.path.join(path_to_fixtures, "model.pickle"), "rb") as model_pickle:
            self.model = pickle.load(model_pickle)


class TestContPlottingFun(Test1DFunctions):
    def test_1D_continuous_line_plot(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
        )
        fig, ax = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        ## effect line
        sns.lineplot(x=ale_eff.index, y=ale_eff["eff"], ax=ax)
        eff_plt_data = ax.lines[0].get_xydata()
        # the x values should be the bins
        self.assertCountEqual(eff_plt_data[:, 0], ale_eff.index)
        # the y values should be the effect
        self.assertCountEqual(eff_plt_data[:, 1], ale_eff.eff)

    def test_1D_continuous_rug_plot(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
        )
        sorted_values = self.X_cleaned["x1"].sort_values()
        values_diff = abs(sorted_values.shift() - sorted_values)

        fig, ax = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        ## the rug
        sns.rugplot(x=self.X_cleaned["x1"], ax=ax)
        rug_plot_data = ax.lines[1].get_xydata()
        # a line for each data point in X
        self.assertEqual(rug_plot_data.shape[0], self.X_cleaned.shape[0])
        # y position is always at the lowest eff value (including the values
        # of the confidence interval)
        self.assertCountEqual(
            np.unique(rug_plot_data[:, 1]),
            [ale_eff.drop("size", axis=1, inplace=False).min().min()],
        )
        # x position should always be plotted within the bin it belongs to
        # (less than the upper bin limit and more than the lower bin limit)
        self.assertTrue(
            np.all(
                ale_eff.index[
                    pd.cut(
                        self.X_cleaned["x1"], ale_eff.index, include_lowest=True
                    ).cat.codes
                    + 1
                ]
                + values_diff[values_diff > 0].min()
                >= rug_plot_data[:, 0]
            )
            and np.all(
                ale_eff.index[
                    pd.cut(
                        self.X_cleaned["x1"], ale_eff.index, include_lowest=True
                    ).cat.codes
                ]
                - values_diff[values_diff > 0].min()
                < rug_plot_data[:, 0]
            )
        )

    def test_1D_continuous_ci_plot(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
        )
        fig, ax = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        sns.lineplot(
            x=ale_eff.index,
            y=ale_eff["eff"],
            ci="sd",
            ax=ax,
        )
        ci_plot_data = (
            pd.DataFrame(ax.collections[0].get_paths()[0].vertices)
            .drop_duplicates()
            .groupby(0)
            .agg(["min", "max"])
        )
        ci_plot_data.index.name = "x1"
        ci_plot_data.columns = ["lowerCI_95%", "upperCI_95%"]
        self.assertTrue(
            np.all(
                ale_eff.loc[ale_eff.index[1] :, ["lowerCI_95%", "upperCI_95%"]]
                == ci_plot_data
            )
        )


class TestDiscPlottingFun(Test1DFunctions):
    def test_1D_continuous_line_plot(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True
        )
        fig, ax, ax2 = plot_1D_discrete_eff(ale_eff, self.X_cleaned)
        sns.lineplot(x=ale_eff.index, y=ale_eff["eff"], ax=ax)
        self.assertCountEqual(ax.lines[0].get_xydata()[:, 0], ale_eff.index)
        self.assertCountEqual(ax.lines[0].get_xydata()[:, 1], ale_eff.eff)

    def test_1D_continuous_ci_plot(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True
        )
        fig, ax, ax2 = plot_1D_discrete_eff(ale_eff, self.X_cleaned)
        sns.lineplot(
            x=ale_eff.index,
            y=ale_eff["eff"],
            ci="sd",
            ax=ax,
        )
        self.assertCountEqual(
            np.round(ax.lines[1].get_xydata()[1:, 1], 8),
            np.round(ale_eff["lowerCI_95%"][1:], 8),
        )
        self.assertCountEqual(
            np.round(ax.lines[2].get_xydata()[1:, 1], 8),
            np.round(ale_eff["upperCI_95%"][1:], 8),
        )

    def test_1D_continuous_bar_plot(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True
        )
        fig, ax, ax2 = plot_1D_discrete_eff(ale_eff, self.X_cleaned)
        sns.barplot(x=ale_eff.index, y=ale_eff["size"], ax=ax2)
        self.assertCountEqual(
            ale_eff["size"], [bar.get_height() for bar in ax2.patches]
        )


if __name__ == "__main__":
    unittest.main()
```

This code replaces `matplotlib`-specific plotting with `seaborn` equivalents while preserving the original functionality and structure.