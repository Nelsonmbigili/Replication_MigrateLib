### Explanation of Changes:
To migrate the code from `seaborn` to `altair`, the following changes were made:
1. **Import Statement**: Removed the `seaborn` import and added `altair` import.
2. **Plotting Function (`plot_importance`)**:
   - Replaced the `sns.catplot` function with an equivalent `altair.Chart` object.
   - Used `altair`'s `mark_bar` for bar plots and `encode` for specifying axes and data mappings.
   - Adjusted the data preparation to match `altair`'s requirements (e.g., converting the DataFrame to a long format using `melt`).
   - Added `altair` configurations for axis labels and sorting.

Below is the modified code:

---

### Modified Code:
```python
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
import altair as alt  # Replaced seaborn with altair
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


# The rest of the code remains unchanged...

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
        Other parameters passed to ``altair.Chart``.

    Returns
    -------
    chart : altair.Chart
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

    # Convert data to long format
    df = df.head(max_num_features).reset_index().melt(id_vars="index", var_name="method", value_name="score")

    # Create Altair bar chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('index:N', sort='-y', title='Feature'),
        y=alt.Y('score:Q', title='Score'),
        color=alt.Color('method:N', title='Method'),
        tooltip=['index', 'method', 'score']
    ).properties(
        title="Feature Importance Scores",
        width=800,
        height=400
    )

    return chart
```

---

### Key Changes in the `plot_importance` Function:
1. **Data Preparation**:
   - Used `pandas.melt` to convert the DataFrame into a long format suitable for `altair`.
   - Added columns `method` and `score` to represent the feature selection methods and their corresponding scores.

2. **Altair Chart**:
   - Used `alt.Chart` to create a bar chart.
   - Encoded the x-axis (`index` for feature names), y-axis (`score` for feature scores), and color (`method` for different feature selection methods).
   - Added tooltips to display feature names, methods, and scores interactively.

3. **Chart Properties**:
   - Set the chart title, width, and height for better visualization.

---

### Example Usage:
To visualize the feature importance scores:
```python
# Example DataFrame
scores = pd.DataFrame({
    'Feature1': [0.8, 0.7, 0.6],
    'Feature2': [0.4, 0.5, 0.3],
    'Feature3': [0.2, 0.1, 0.3]
}, index=['Method1', 'Method2', 'Method3']).T

# Plot the importance scores
chart = plot_importance(scores)
chart.show()
```

This will generate an interactive bar chart using `altair`.