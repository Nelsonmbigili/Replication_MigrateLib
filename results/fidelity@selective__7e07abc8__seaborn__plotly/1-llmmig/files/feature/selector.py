#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright FMR LLC <opensource@fidelity.com>
# SPDX-License-Identifier: Apache-2.0

"""
This module defines the public interface of the **Selective Library** for feature selection.
"""

import multiprocessing as mp
from time import time
from typing import Dict, Union, NamedTuple, NoReturn, Tuple, Optional
import numpy as np
import pandas as pd
import plotly.express as px  # Updated import for Plotly
from catboost import CatBoostClassifier, CatBoostRegressor
from joblib import Parallel, delayed
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import KFold
from textwiser import TextWiser, Embedding, Transformation
from xgboost import XGBClassifier, XGBRegressor
from feature.base import _BaseDispatcher, _BaseSupervisedSelector, _BaseUnsupervisedSelector
from feature.correlation import _Correlation
from feature.linear import _Linear
from feature.statistical import _Statistical
from feature.text_based import _TextBased
from feature.tree_based import _TreeBased
from feature.utils import Num, check_true, Constants, normalize_columns
from feature.variance import _Variance
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


__author__ = "FMR LLC"
__version__ = "1.0.0"
__copyright__ = "Copyright (C), FMR LLC"


# Other classes and functions remain unchanged...


def plot_importance(scores: pd.DataFrame,
                    columns: Optional[list] = None,
                    max_num_features: Optional[int] = None,
                    normalize: Optional[str] = None,
                    ignore_constant: Optional[bool] = True,
                    **kwargs):
    """Plot feature selector scores.

    Parameters
    ----------
    scores: pd.DataFrame
        Data frame with scores for each feature (index) and method (columns).
        Each feature could have multiple rows from different cross-validation folds.
    columns: list (default=None)
        List of methods (columns) to include in statistics.
        If None, all methods (columns) will be used.
    max_num_features: int or None, optional (default=None)
        Max number of top features displayed on plot.
        If None all features will be displayed.
    normalize: bool, optional (default=False)
        Whether to normalize scores such that scores sum to 1 for each column.
        This ensures that scores are comparable between different methods.
    ignore_constant: bool, optional (default=True)
        Whether to ignore columns with the same score for all features.
    **kwargs
        Other parameters passed to ``plotly.express.bar``.

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The plot with feature scores.
    """

    check_true(isinstance(scores, pd.DataFrame), ValueError("Selector scores must be a data frame."))

    # Get columns to use
    if columns is None:
        columns = scores.columns

    # Make copy of data frame
    # Fill nan with zero
    df = scores[columns].copy()
    df.fillna(0, inplace=True)

    # Group by feature for CV results
    df = df.groupby(df.index).mean()

    # Get normalized scores such that scores for each method sums to 1
    if normalize:
        df = normalize_columns(df)

    # Drop methods with constant scores
    if ignore_constant:
        mask = ~np.isclose(np.var(df, axis=0), 0)
        df = df.loc[:, mask]

    # Set max_num_features to total number of features if None
    if max_num_features is None:
        max_num_features = len(df)

    # Calculate the mean score and sort in descending order
    mean_score = np.mean(df, axis=1)
    index = (-mean_score).argsort().values
    df = df.iloc[index, :]

    # Convert data to long format for Plotly
    df = df.head(max_num_features).reset_index().melt(id_vars="index", var_name="method", value_name="score")

    # Create bar plot using Plotly
    fig = px.bar(df, x="index", y="score", color="method", barmode="group", **kwargs)
    fig.update_layout(
        xaxis_title="Feature",
        yaxis_title="Score",
        title="Feature Importance Scores",
        legend_title="Method",
        template="plotly_white"
    )

    return fig
# Example usage of the updated plot_importance function
import pandas as pd

# Example scores DataFrame
scores = pd.DataFrame({
    "Feature1": [0.8, 0.6, 0.7],
    "Feature2": [0.4, 0.5, 0.3],
    "Feature3": [0.9, 0.8, 0.85]
}, index=["Method1", "Method2", "Method3"]).T

# Plot feature importance
fig = plot_importance(scores, max_num_features=2)
fig.show()
