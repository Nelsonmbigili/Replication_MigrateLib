import unittest
import os
import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from PyALE._src.ALE_1D import (
    aleplot_1D_continuous,
    aleplot_1D_discrete,
    aleplot_1D_categorical,
)
import plotly.graph_objects as go  # Importing Plotly for plotting


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


# Updated plotting function for continuous effects
def plot_1D_continuous_eff(ale_eff, X_cleaned):
    fig = go.Figure()

    # Add effect line
    fig.add_trace(
        go.Scatter(
            x=ale_eff.index,
            y=ale_eff["eff"],
            mode="lines",
            name="Effect",
            line=dict(color="blue"),
        )
    )

    # Add confidence interval (if present)
    if "lowerCI_95%" in ale_eff.columns and "upperCI_95%" in ale_eff.columns:
        fig.add_trace(
            go.Scatter(
                x=list(ale_eff.index) + list(ale_eff.index[::-1]),
                y=list(ale_eff["upperCI_95%"]) + list(ale_eff["lowerCI_95%"][::-1]),
                fill="toself",
                fillcolor="rgba(0,100,200,0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="95% CI",
            )
        )

    # Add rug plot
    fig.add_trace(
        go.Scatter(
            x=X_cleaned["x1"],
            y=[ale_eff["eff"].min()] * len(X_cleaned),
            mode="markers",
            marker=dict(symbol="line-ns-open", color="black"),
            name="Rug",
        )
    )

    fig.update_layout(
        title="1D Continuous Effect Plot",
        xaxis_title="Feature",
        yaxis_title="Effect",
        template="plotly_white",
    )
    return fig


# Updated plotting function for discrete effects
def plot_1D_discrete_eff(ale_eff, X_cleaned):
    fig = go.Figure()

    # Add effect line
    fig.add_trace(
        go.Scatter(
            x=ale_eff.index,
            y=ale_eff["eff"],
            mode="lines+markers",
            name="Effect",
            line=dict(color="blue"),
        )
    )

    # Add confidence intervals (if present)
    if "lowerCI_95%" in ale_eff.columns and "upperCI_95%" in ale_eff.columns:
        fig.add_trace(
            go.Scatter(
                x=ale_eff.index,
                y=ale_eff["lowerCI_95%"],
                mode="lines",
                line=dict(dash="dash", color="gray"),
                name="Lower CI",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=ale_eff.index,
                y=ale_eff["upperCI_95%"],
                mode="lines",
                line=dict(dash="dash", color="gray"),
                name="Upper CI",
            )
        )

    # Add bar plot for sizes
    fig.add_trace(
        go.Bar(
            x=ale_eff.index,
            y=ale_eff["size"],
            name="Size",
            marker=dict(color="rgba(100,150,200,0.6)"),
            yaxis="y2",
        )
    )

    fig.update_layout(
        title="1D Discrete Effect Plot",
        xaxis_title="Feature",
        yaxis_title="Effect",
        yaxis2=dict(
            title="Size",
            overlaying="y",
            side="right",
        ),
        template="plotly_white",
    )
    return fig


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


class Test1DContinuous(Test1DFunctions):
    def test_indexname(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=False,
        )
        self.assertEqual(ale_eff.index.name, "x1")

    def test_outputshape_noCI(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=False,
        )
        self.assertEqual(ale_eff.shape, (6, 2))
        self.assertCountEqual(ale_eff.columns, ["eff", "size"])

    def test_outputshape_withCI(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
            C=0.9,
        )
        self.assertEqual(ale_eff.shape, (6, 4))
        self.assertCountEqual(
            ale_eff.columns, ["eff", "size", "lowerCI_90%", "upperCI_90%"]
        )

    def test_bins(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=False,
        )
        self.assertCountEqual(
            ale_eff.index,
            [
                0.0013107121819164735,
                0.21205399821897986,
                0.3905585553320686,
                0.5561380185409515,
                0.7797798975036754,
                0.9986526271693825,
            ],
        )

    def test_effvalues(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=False,
        )
        self.assertCountEqual(
            np.round(ale_eff.loc[:, "eff"], 8),
            [-0.3302859, -0.25946135, -0.03809224, 0.03292833, 0.27153761, 0.3164612],
        )

    def test_binsizes(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=False,
        )
        self.assertCountEqual(
            ale_eff.loc[:, "size"], [0.0, 40.0, 40.0, 40.0, 40.0, 40.0]
        )

    def test_CIvalues(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
            C=0.9,
        )
        # assert that the first bin do not have a CI
        self.assertTrue(np.isnan(ale_eff.loc[ale_eff.index[0], "lowerCI_90%"]))
        self.assertTrue(np.isnan(ale_eff.loc[ale_eff.index[0], "upperCI_90%"]))
        # check the values of the CI
        self.assertCountEqual(
            np.round(ale_eff.loc[ale_eff.index[1] :, "lowerCI_90%"], 8),
            [-0.37210104, -0.08077478, -0.00175768, 0.20772107, 0.24621853],
        )
        self.assertCountEqual(
            np.round(ale_eff.loc[ale_eff.index[1] :, "upperCI_90%"], 8),
            [-0.14682166, 0.00459031, 0.06761434, 0.33535415, 0.38670386],
        )

    def test_exceptions(self):
        # dataset should be compatible with the model
        with self.assertRaises(Exception) as mod_ex_2:
            aleplot_1D_continuous(self.X, self.model, "x1")
        mod_ex_msg = "Please check that your model is fitted, and accepts X as input."
        self.assertEqual(mod_ex_2.exception.args[0], mod_ex_msg)


class Test1Ddiscrete(Test1DFunctions):
    def test_indexname(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=False
        )
        self.assertEqual(ale_eff.index.name, "x4")

    def test_outputshape_noCI(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=False
        )
        self.assertEqual(ale_eff.shape, (10, 2))
        self.assertCountEqual(ale_eff.columns, ["eff", "size"])

    def test_outputshape_withCI(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True, C=0.9
        )
        self.assertEqual(ale_eff.shape, (10, 4))
        self.assertCountEqual(
            ale_eff.columns, ["eff", "size", "lowerCI_90%", "upperCI_90%"]
        )

    def test_bins(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=False
        )
        self.assertCountEqual(
            ale_eff.index,
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        )

    def test_effvalues(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=False
        )
        self.assertCountEqual(
            np.round(ale_eff.loc[:, "eff"], 8),
            [
                -1.15833245,
                -0.87518863,
                -0.17627267,
                -0.03183705,
                0.21772015,
                0.3103579,
                0.37654819,
                0.38187692,
                0.54013521,
                0.59118777,
            ],
        )

    def test_binsizes(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=False
        )
        self.assertCountEqual(
            ale_eff.loc[:, "size"], [27, 14, 16, 26, 20, 17, 18, 23, 21, 18]
        )

    def test_CIvalues(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True, C=0.9
        )
        # assert that the first bin do not have a CI
        self.assertTrue(np.isnan(ale_eff.loc[ale_eff.index[0], "lowerCI_90%"]))
        self.assertTrue(np.isnan(ale_eff.loc[ale_eff.index[0], "upperCI_90%"]))
        # check the values of the CI
        self.assertCountEqual(
            np.round(ale_eff.loc[ale_eff.index[1] :, "lowerCI_90%"], 8),
            [
                -0.92693686,
                -0.30837293,
                -0.05872927,
                0.17298345,
                0.23835091,
                0.34097451,
                0.35996381,
                0.47381797,
                0.56927921,
            ],
        )
        self.assertCountEqual(
            np.round(ale_eff.loc[ale_eff.index[1] :, "upperCI_90%"], 8),
            [
                -0.8234404,
                -0.0441724,
                -0.00494484,
                0.26245684,
                0.38236488,
                0.41212186,
                0.40379003,
                0.60645245,
                0.61309633,
            ],
        )

    def test_exceptions(self):
        mod_not_fit = RandomForestRegressor()
        # dataset should be compatible with the model
        with self.assertRaises(Exception) as mod_ex_2:
            aleplot_1D_discrete(self.X, mod_not_fit, "x4")
        mod_ex_msg = "Please check that your model is fitted, and accepts X as input."
        self.assertEqual(mod_ex_2.exception.args[0], mod_ex_msg)


class Test1Ddiscrete(Test1DFunctions):
    def test_indexname(self):
        ale_eff = aleplot_1D_categorical(
            X=self.X,
            model=self.model,
            feature="x5",
            predictors=self.X_cleaned.columns,
            encode_fun=onehot_encode_custom,
            include_CI=False,
        )
        self.assertEqual(ale_eff.index.name, "x5")

    def test_outputshape_noCI(self):
        ale_eff = aleplot_1D_categorical(
            X=self.X,
            model=self.model,
            feature="x5",
            predictors=self.X_cleaned.columns,
            encode_fun=onehot_encode_custom,
            include_CI=False,
        )
        self.assertEqual(ale_eff.shape, (3, 2))
        self.assertCountEqual(ale_eff.columns, ["eff", "size"])

    def test_outputshape_withCI(self):
        ale_eff = aleplot_1D_categorical(
            X=self.X,
            model=self.model,
            feature="x5",
            predictors=self.X_cleaned.columns,
            encode_fun=onehot_encode_custom,
            include_CI=True,
            C=0.9,
        )
        self.assertEqual(ale_eff.shape, (3, 4))
        self.assertCountEqual(
            ale_eff.columns, ["eff", "size", "lowerCI_90%", "upperCI_90%"]
        )

    def test_bins(self):
        ale_eff = aleplot_1D_categorical(
            X=self.X,
            model=self.model,
            feature="x5",
            predictors=self.X_cleaned.columns,
            encode_fun=onehot_encode_custom,
            include_CI=False,
        )
        self.assertCountEqual(
            ale_eff.index,
            ["A", "B", "C"],
        )

    def test_effvalues(self):
        ale_eff = aleplot_1D_categorical(
            X=self.X,
            model=self.model,
            feature="x5",
            predictors=self.X_cleaned.columns,
            encode_fun=onehot_encode_custom,
            include_CI=False,
        )
        self.assertCountEqual(
            np.round(ale_eff.loc[:, "eff"], 8),
            [-0.05565697, 0.02367971, 0.02044105],
        )

    def test_binsizes(self):
        ale_eff = aleplot_1D_categorical(
            X=self.X,
            model=self.model,
            feature="x5",
            predictors=self.X_cleaned.columns,
            encode_fun=onehot_encode_custom,
            include_CI=False,
        )
        self.assertCountEqual(ale_eff.loc[:, "size"], [57, 77, 66])

    def test_CIvalues(self):
        ale_eff = aleplot_1D_categorical(
            X=self.X,
            model=self.model,
            feature="x5",
            predictors=self.X_cleaned.columns,
            encode_fun=onehot_encode_custom,
            include_CI=True,
            C=0.9,
        )
        # assert that the first bin do not have a CI
        self.assertTrue(np.isnan(ale_eff.loc[ale_eff.index[0], "lowerCI_90%"]))
        self.assertTrue(np.isnan(ale_eff.loc[ale_eff.index[0], "upperCI_90%"]))
        # check the values of the CI
        self.assertCountEqual(
            np.round(ale_eff.loc[ale_eff.index[1] :, "lowerCI_90%"], 8),
            [-0.00605249, -0.00523023],
        )
        self.assertCountEqual(
            np.round(ale_eff.loc[ale_eff.index[1] :, "upperCI_90%"], 8),
            [0.05341192, 0.04611233],
        )

    def test_exceptions(self):
        mod_not_fit = RandomForestRegressor()
        # dataset should be compatible with the model
        with self.assertRaises(Exception) as mod_ex_1:
            aleplot_1D_categorical(
                X=self.X,
                model=self.model.predict,
                feature="x5",
                predictors=self.X_cleaned.columns,
                encode_fun=onehot_encode_custom,
            )
        with self.assertRaises(Exception) as mod_ex_2:
            aleplot_1D_categorical(
                X=self.X,
                model=self.model,
                feature="x5",
                predictors=self.X.columns,
                encode_fun=onehot_encode_custom,
            )
        with self.assertRaises(Exception) as mod_ex_3:
            aleplot_1D_categorical(
                X=self.X,
                model=self.model,
                feature="x5",
                predictors=self.X_cleaned.columns,
                encode_fun=onehot_encode,
            )
        mod_ex_msg = (
            """There seems to be a problem when predicting with the model.
            Please check the following: 
                - Your model is fitted.
                - The list of predictors contains the names of all the features"""
            """ used for training the model.
                - The encoding function takes the raw feature and returns the"""
            """ right columns encoding it, including the case of a missing category.
            """
        )
        self.assertEqual(mod_ex_1.exception.args[0], mod_ex_msg)
        self.assertEqual(mod_ex_2.exception.args[0], mod_ex_msg)
        self.assertEqual(mod_ex_3.exception.args[0], mod_ex_msg)


class TestContPlottingFun(Test1DFunctions):
    def test_1D_continuous_line_plot(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
        )
        fig = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        # Test the effect line
        effect_line = fig.data[0]
        self.assertCountEqual(effect_line.x, ale_eff.index)
        self.assertCountEqual(effect_line.y, ale_eff["eff"])

    def test_1D_continuous_ci_plot(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
        )
        fig = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        ci_fill = fig.data[1]
        self.assertTrue("95% CI" in ci_fill.name)

    def test_1D_continuous_rug_plot(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
        )
        fig = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        sorted_values = self.X_cleaned["x1"].sort_values()
        values_diff = abs(sorted_values.shift() - sorted_values)

        fig, ax = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        ## the rug
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
        rug_plot = fig.data[2]
        self.assertEqual(len(rug_plot.x), len(self.X_cleaned))


class TestDiscPlottingFun(Test1DFunctions):
    def test_1D_discrete_line_plot(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True
        )
        fig = plot_1D_discrete_eff(ale_eff, self.X_cleaned)
        effect_line = fig.data[0]
        self.assertCountEqual(effect_line.x, ale_eff.index)
        self.assertCountEqual(effect_line.y, ale_eff["eff"])

    def test_1D_discrete_ci_plot(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True
        )
        fig = plot_1D_discrete_eff(ale_eff, self.X_cleaned)
        lower_ci = fig.data[1]
        upper_ci = fig.data[2]
        self.assertCountEqual(lower_ci.y, ale_eff["lowerCI_95%"])
        self.assertCountEqual(upper_ci.y, ale_eff["upperCI_95%"])

    def test_1D_discrete_bar_plot(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True
        )
        fig = plot_1D_discrete_eff(ale_eff, self.X_cleaned)
        bar_plot = fig.data[3]
        self.assertCountEqual(bar_plot.y, ale_eff["size"])


if __name__ == "__main__":
    unittest.main()