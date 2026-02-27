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
