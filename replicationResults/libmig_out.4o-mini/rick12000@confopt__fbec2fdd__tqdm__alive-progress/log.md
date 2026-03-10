## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/rick12000@confopt__fbec2fdd__tqdm__alive-progress/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating confopt/tuning.py
### migrating tests/test_tuning.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_tuning.py::test_random_search: passed != failed`
- `tests/test_tuning.py::test_search: passed != failed`
- `tests/test_tuning.py::test_search__reproducibility: passed != failed`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 4, cov finished with status 1
### test diff with round premig
- `tests/test_estimation.py::test_cross_validate_configurations__point_estimator: passed != not found`
- `tests/test_estimation.py::test_cross_validate_configurations__point_estimator__reproducibility: passed != not found`
- `tests/test_estimation.py::test_initialize_point_estimator: passed != not found`
- `tests/test_estimation.py::test_initialize_point_estimator__reproducibility: passed != not found`
- `tests/test_estimation.py::test_initialize_quantile_estimator: passed != not found`
- `tests/test_estimation.py::test_initialize_quantile_estimator__reproducibility: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-gbm-0-0.2]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-gbm-0-0.8]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-gbm-1-0.2]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-gbm-1-0.8]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-gbm-3-0.2]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-gbm-3-0.8]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-rf-0-0.2]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-rf-0-0.8]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-rf-1-0.2]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-rf-1-0.8]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-rf-3-0.2]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__fit[gbm-gbm-rf-3-0.8]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__predict[gbm-gbm-gbm-5-0.2]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__predict[gbm-gbm-gbm-5-0.8]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__predict[gbm-gbm-rf-5-0.2]: passed != not found`
- `tests/test_estimation.py::test_locally_weighted_conformal_regression__predict[gbm-gbm-rf-5-0.8]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qgbm-0-0.2]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qgbm-0-0.8]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qgbm-1-0.2]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qgbm-1-0.8]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qgbm-3-0.2]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qgbm-3-0.8]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qrf-0-0.2]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qrf-0-0.8]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qrf-1-0.2]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qrf-1-0.8]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qrf-3-0.2]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__fit[qrf-3-0.8]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__predict[qgbm-5-0.2]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__predict[qgbm-5-0.8]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__predict[qrf-5-0.2]: passed != not found`
- `tests/test_estimation.py::test_quantile_conformal_regression__predict[qrf-5-0.8]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[1-0.5-1-100]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[1-0.5-1-1]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[1-0.5-100-100]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[1-0.5-100-1]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[1-2-1-100]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[1-2-1-1]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[1-2-100-100]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[1-2-100-1]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[10-0.5-1-100]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[10-0.5-1-1]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[10-0.5-100-100]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[10-0.5-100-1]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[10-2-1-100]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[10-2-1-1]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[10-2-100-100]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count[10-2-100-1]: passed != not found`
- `tests/test_optimization.py::test_derive_optimal_tuning_count__no_iterations: passed != not found`
- `tests/test_optimization.py::test_runtime_tracker__pause_runtime: passed != not found`
- `tests/test_optimization.py::test_runtime_tracker__return_runtime: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[False-False-0.25]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[False-False-0.5]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[False-False-0.75]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[False-True-0.25]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[False-True-0.5]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[False-True-0.75]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[True-False-0.25]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[True-False-0.5]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[True-False-0.75]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[True-True-0.25]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[True-True-0.5]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split[True-True-0.75]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[False-False-0.25]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[False-False-0.5]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[False-False-0.75]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[False-True-0.25]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[False-True-0.5]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[False-True-0.75]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[True-False-0.25]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[True-False-0.5]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[True-False-0.75]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[True-True-0.25]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[True-True-0.5]: passed != not found`
- `tests/test_preprocessing.py::test_train_val_split__reproducibility[True-True-0.75]: passed != not found`
- `tests/test_tuning.py::test_evaluate_configuration_performance: passed != not found`
- `tests/test_tuning.py::test_evaluate_configuration_performance__reproducibility: passed != not found`
- `tests/test_tuning.py::test_get_best_configuration_idx[direct]: passed != not found`
- `tests/test_tuning.py::test_get_best_configuration_idx[inverse]: passed != not found`
- `tests/test_tuning.py::test_get_tuning_configurations: passed != not found`
- `tests/test_tuning.py::test_get_tuning_configurations__reproducibility: passed != not found`
- `tests/test_tuning.py::test_normalize_estimation_data: passed != not found`
- `tests/test_tuning.py::test_process_and_split_estimation_data: passed != not found`
- `tests/test_tuning.py::test_process_and_split_estimation_data__reproducibility: passed != not found`
- `tests/test_tuning.py::test_random_search: passed != not found`
- `tests/test_tuning.py::test_random_search__reproducibility: passed != not found`
- `tests/test_tuning.py::test_score_predictions__perfect_score[accuracy_score]: passed != not found`
- `tests/test_tuning.py::test_score_predictions__perfect_score[log_loss]: passed != not found`
- `tests/test_tuning.py::test_score_predictions__perfect_score[mean_squared_error]: passed != not found`
- `tests/test_tuning.py::test_search: passed != not found`
- `tests/test_tuning.py::test_search__reproducibility: passed != not found`
- `tests/test_tuning.py::test_update_adaptive_interval[0.01-0.2-False]: passed != not found`
- `tests/test_tuning.py::test_update_adaptive_interval[0.01-0.2-True]: passed != not found`
- `tests/test_tuning.py::test_update_adaptive_interval[0.01-0.8-False]: passed != not found`
- `tests/test_tuning.py::test_update_adaptive_interval[0.01-0.8-True]: passed != not found`
- `tests/test_tuning.py::test_update_adaptive_interval[0.1-0.2-False]: passed != not found`
- `tests/test_tuning.py::test_update_adaptive_interval[0.1-0.2-True]: passed != not found`
- `tests/test_tuning.py::test_update_adaptive_interval[0.1-0.8-False]: passed != not found`
- `tests/test_tuning.py::test_update_adaptive_interval[0.1-0.8-True]: passed != not found`
- `tests/test_utils.py::test_get_perceptron_layers: passed != not found`
- `tests/test_utils.py::test_get_perceptron_layers__reproducibility: passed != not found`
- `tests/test_utils.py::test_get_tuning_configurations: passed != not found`
- `tests/test_utils.py::test_get_tuning_configurations__reproducibility: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
