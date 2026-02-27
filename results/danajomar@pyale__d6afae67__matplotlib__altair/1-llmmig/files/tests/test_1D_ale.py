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
import altair as alt


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


def plot_1D_continuous_eff(ale_eff, X_cleaned):
    """
    Altair-based plotting function for 1D continuous ALE effects.
    """
    # Prepare data for Altair
    ale_eff = ale_eff.reset_index()
    rug_data = pd.DataFrame({"x1": X_cleaned["x1"]})

    # Line plot for ALE effect
    line = alt.Chart(ale_eff).mark_line().encode(
        x=alt.X("x1:Q", title="Feature (x1)"),
        y=alt.Y("eff:Q", title="ALE Effect"),
    )

    # Rug plot
    rug = alt.Chart(rug_data).mark_tick(color="black", thickness=1).encode(
        x=alt.X("x1:Q", title=None),
        y=alt.value(0),  # Position the rug at y=0
    )

    # Confidence interval area
    if "lowerCI_90%" in ale_eff.columns and "upperCI_90%" in ale_eff.columns:
        ci = alt.Chart(ale_eff).mark_area(opacity=0.3).encode(
            x=alt.X("x1:Q"),
            y=alt.Y("lowerCI_90%:Q", title="Confidence Interval"),
            y2=alt.Y2("upperCI_90%:Q"),
        )
        chart = ci + line + rug
    else:
        chart = line + rug

    return chart


def plot_1D_discrete_eff(ale_eff, X_cleaned):
    """
    Altair-based plotting function for 1D discrete ALE effects.
    """
    # Prepare data for Altair
    ale_eff = ale_eff.reset_index()

    # Bar plot for bin sizes
    bars = alt.Chart(ale_eff).mark_bar().encode(
        x=alt.X("x4:O", title="Feature (x4)"),
        y=alt.Y("size:Q", title="Bin Size"),
    )

    # Line plot for ALE effect
    line = alt.Chart(ale_eff).mark_line(color="red").encode(
        x=alt.X("x4:O"),
        y=alt.Y("eff:Q", title="ALE Effect"),
    )

    # Confidence interval lines
    if "lowerCI_90%" in ale_eff.columns and "upperCI_90%" in ale_eff.columns:
        ci = alt.Chart(ale_eff).mark_errorbar(extent="ci").encode(
            x=alt.X("x4:O"),
            y=alt.Y("lowerCI_90%:Q"),
            y2=alt.Y2("upperCI_90%:Q"),
        )
        chart = bars + line + ci
    else:
        chart = bars + line

    return chart


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
        chart = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        self.assertIsInstance(chart, alt.Chart)

    def test_1D_continuous_ci_plot(self):
        ale_eff = aleplot_1D_continuous(
            X=self.X_cleaned,
            model=self.model,
            feature="x1",
            grid_size=5,
            include_CI=True,
        )
        chart = plot_1D_continuous_eff(ale_eff, self.X_cleaned)
        self.assertIsInstance(chart, alt.Chart)


class TestDiscPlottingFun(Test1DFunctions):
    def test_1D_discrete_bar_plot(self):
        ale_eff = aleplot_1D_discrete(
            X=self.X_cleaned, model=self.model, feature="x4", include_CI=True
        )
        chart = plot_1D_discrete_eff(ale_eff, self.X_cleaned)
        self.assertIsInstance(chart, alt.Chart)


if __name__ == "__main__":
    unittest.main()
