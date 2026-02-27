import random
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest
import progressbar  # Replaced tqdm with progressbar2

from confopt.config import GBM_NAME
from confopt.optimization import RuntimeTracker
from confopt.tuning import (
    score_predictions,
    get_best_configuration_idx,
    process_and_split_estimation_data,
    normalize_estimation_data,
    update_adaptive_confidence_level,
)

DEFAULT_SEED = 1234


@pytest.mark.parametrize("optimization_direction", ["direct", "inverse"])
def test_get_best_configuration_idx(optimization_direction):
    lower_bound = np.array([5, 4, 3, 2, 1])
    higher_bound = lower_bound + 1
    dummy_performance_bounds = (lower_bound, higher_bound)

    best_idx = get_best_configuration_idx(
        configuration_performance_bounds=dummy_performance_bounds,
        optimization_direction=optimization_direction,
    )

    assert best_idx >= 0
    if optimization_direction == "direct":
        assert best_idx == np.argmax(higher_bound)
    elif optimization_direction == "inverse":
        assert best_idx == np.argmin(lower_bound)


@pytest.mark.parametrize(
    "scoring_function", ["accuracy_score", "mean_squared_error", "log_loss"]
)
def test_score_predictions__perfect_score(scoring_function):
    dummy_y_obs = np.array([1, 0, 1, 0, 1, 1])
    dummy_y_pred = deepcopy(dummy_y_obs)

    score = score_predictions(
        y_obs=dummy_y_obs, y_pred=dummy_y_pred, scoring_function=scoring_function
    )

    if scoring_function == "accuracy_score":
        assert score == 1
    elif scoring_function == "mean_squared_error":
        assert score == 0
    elif scoring_function == "log_loss":
        assert 0 < score < 0.001


def test_process_and_split_estimation_data(dummy_configurations):
    train_split = 0.5
    dummy_searched_configurations = pd.DataFrame(dummy_configurations).to_numpy()
    stored_dummy_searched_configurations = deepcopy(dummy_searched_configurations)
    dummy_searched_performances = np.array(
        [random.random() for _ in range(len(dummy_configurations))]
    )
    stored_dummy_searched_performances = deepcopy(dummy_searched_performances)

    X_train, y_train, X_val, y_val = process_and_split_estimation_data(
        searched_configurations=dummy_searched_configurations,
        searched_performances=dummy_searched_performances,
        train_split=train_split,
        filter_outliers=False,
        outlier_scope=None,
        random_state=DEFAULT_SEED,
    )

    assert len(X_val) == len(y_val)
    assert len(X_train) == len(y_train)

    assert len(X_val) + len(X_train) == len(dummy_searched_configurations)

    assert (
        abs(len(X_train) - round(len(dummy_searched_configurations) * train_split)) <= 1
    )
    assert (
        abs(len(X_val) - round(len(dummy_searched_configurations) * (1 - train_split)))
        <= 1
    )

    # Assert there is no mutability of input:
    assert np.array_equal(
        dummy_searched_configurations, stored_dummy_searched_configurations
    )
    assert np.array_equal(
        dummy_searched_performances, stored_dummy_searched_performances
    )


def test_random_search(dummy_initialized_conformal_searcher__gbm_mse):
    n_searches = 5
    max_runtime = 30
    dummy_initialized_conformal_searcher__gbm_mse.search_timer = RuntimeTracker()

    # Initialize progress bar
    progress = progressbar.ProgressBar(max_value=n_searches).start()

    (
        searched_configurations,
        searched_performances,
        runtime_per_search,
    ) = dummy_initialized_conformal_searcher__gbm_mse._random_search(
        n_searches=n_searches,
        max_runtime=max_runtime,
        random_state=DEFAULT_SEED,
        progress_callback=lambda i: progress.update(i + 1),  # Update progress bar
    )

    progress.finish()  # Finish the progress bar

    for performance in searched_performances:
        assert performance > 0
    assert len(searched_configurations) > 0
    assert len(searched_performances) > 0
    assert len(searched_configurations) == len(searched_performances)
    assert len(searched_configurations) == n_searches
    assert 0 < runtime_per_search < max_runtime


def test_random_search__reproducibility(
    dummy_initialized_conformal_searcher__gbm_mse,
):
    n_searches = 5
    max_runtime = 30
    dummy_initialized_conformal_searcher__gbm_mse.search_timer = RuntimeTracker()

    (
        searched_configurations_first_call,
        searched_performances_first_call,
        _,
    ) = dummy_initialized_conformal_searcher__gbm_mse._random_search(
        n_searches=n_searches,
        max_runtime=max_runtime,
        random_state=DEFAULT_SEED,
    )
    (
        searched_configurations_second_call,
        searched_performances_second_call,
        _,
    ) = dummy_initialized_conformal_searcher__gbm_mse._random_search(
        n_searches=n_searches,
        max_runtime=max_runtime,
        random_state=DEFAULT_SEED,
    )

    assert searched_configurations_first_call == searched_configurations_second_call
    assert searched_performances_first_call == searched_performances_second_call
