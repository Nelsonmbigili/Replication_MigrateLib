## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/spiketools@spiketools__3df1ec3a__matplotlib__plotly/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 14 files
### migrating spiketools/plts/annotate.py
### migrating spiketools/plts/data.py
### migrating spiketools/plts/settings.py
### migrating spiketools/plts/spatial.py
### migrating spiketools/plts/spikes.py
### migrating spiketools/plts/stats.py
### migrating spiketools/plts/style.py
### migrating spiketools/plts/task.py
### migrating spiketools/plts/trials.py
### migrating spiketools/plts/utils.py
### migrating spiketools/tests/plts/test_annotate.py
### migrating spiketools/tests/plts/test_style.py
### migrating spiketools/tests/plts/test_utils.py
### migrating spiketools/tests/tutils.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `spiketools/tests/measures/test_circular.py::test_bin_circular: passed != not found`
- `spiketools/tests/measures/test_collections.py::test_detect_empty_time_ranges: passed != not found`
- `spiketools/tests/measures/test_collections.py::test_find_empty_bins: passed != not found`
- `spiketools/tests/measures/test_collections.py::test_find_empty_ranges: passed != not found`
- `spiketools/tests/measures/test_conversions.py::test_convert_isis_to_times: passed != not found`
- `spiketools/tests/measures/test_conversions.py::test_convert_times_to_counts: passed != not found`
- `spiketools/tests/measures/test_conversions.py::test_convert_times_to_rates: passed != not found`
- `spiketools/tests/measures/test_conversions.py::test_convert_times_to_train: passed != not found`
- `spiketools/tests/measures/test_conversions.py::test_convert_train_to_times: passed != not found`
- `spiketools/tests/measures/test_spikes.py::test_compute_cv: passed != not found`
- `spiketools/tests/measures/test_spikes.py::test_compute_fano_factor: passed != not found`
- `spiketools/tests/measures/test_spikes.py::test_compute_firing_rate: passed != not found`
- `spiketools/tests/measures/test_spikes.py::test_compute_isis: passed != not found`
- `spiketools/tests/measures/test_spikes.py::test_compute_presence_ratio: passed != not found`
- `spiketools/tests/measures/test_spikes.py::test_compute_spike_presence: passed != not found`
- `spiketools/tests/measures/test_trials.py::test_compute_pre_post_averages: passed != not found`
- `spiketools/tests/measures/test_trials.py::test_compute_pre_post_diffs: passed != not found`
- `spiketools/tests/measures/test_trials.py::test_compute_pre_post_rates: passed != not found`
- `spiketools/tests/measures/test_trials.py::test_compute_segment_frs: passed != not found`
- `spiketools/tests/measures/test_trials.py::test_compute_trial_frs: passed != not found`
- `spiketools/tests/modutils/test_dependencies.py::test_check_dependency: passed != not found`
- `spiketools/tests/modutils/test_dependencies.py::test_safe_import: passed != not found`
- `spiketools/tests/modutils/test_functions.py::test_get_function_argument: passed != not found`
- `spiketools/tests/modutils/test_functions.py::test_get_function_parameters: passed != not found`
- `spiketools/tests/objects/test_session.py::test_session: passed != not found`
- `spiketools/tests/objects/test_session.py::test_session_add_unit: passed != not found`
- `spiketools/tests/objects/test_unit.py::test_unit: passed != not found`
- `spiketools/tests/objects/test_unit.py::test_unit_cv: passed != not found`
- `spiketools/tests/objects/test_unit.py::test_unit_fano: passed != not found`
- `spiketools/tests/objects/test_unit.py::test_unit_firing_rate: passed != not found`
- `spiketools/tests/objects/test_unit.py::test_unit_isis: passed != not found`
- `spiketools/tests/objects/test_unit.py::test_unit_shuffle: passed != not found`
- `spiketools/tests/objects/test_unit.py::test_unit_spike_train: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_box_shade: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_box_shades: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_dots: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_gridlines: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_hlines: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_hshades: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_significance: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_text_labels_x: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_text_labels_y: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_vlines: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_add_vshades: passed != not found`
- `spiketools/tests/plts/test_annotate.py::test_color_pvalue: passed != not found`
- `spiketools/tests/plts/test_data.py::test_plot_bar: passed != not found`
- `spiketools/tests/plts/test_data.py::test_plot_barh: passed != not found`
- `spiketools/tests/plts/test_data.py::test_plot_hist: passed != not found`
- `spiketools/tests/plts/test_data.py::test_plot_lines: passed != not found`
- `spiketools/tests/plts/test_data.py::test_plot_points: passed != not found`
- `spiketools/tests/plts/test_data.py::test_plot_polar_hist: passed != not found`
- `spiketools/tests/plts/test_data.py::test_plot_scatter: passed != not found`
- `spiketools/tests/plts/test_spatial.py::test_create_heatmap_title: passed != not found`
- `spiketools/tests/plts/test_spatial.py::test_plot_heatmap: passed != not found`
- `spiketools/tests/plts/test_spatial.py::test_plot_position_1d: passed != not found`
- `spiketools/tests/plts/test_spatial.py::test_plot_position_by_time: passed != not found`
- `spiketools/tests/plts/test_spatial.py::test_plot_positions: passed != not found`
- `spiketools/tests/plts/test_spatial.py::test_plot_trial_heatmaps: passed != not found`
- `spiketools/tests/plts/test_spikes.py::test_plot_firing_rates: passed != not found`
- `spiketools/tests/plts/test_spikes.py::test_plot_isis: passed != not found`
- `spiketools/tests/plts/test_spikes.py::test_plot_waveform: passed != not found`
- `spiketools/tests/plts/test_spikes.py::test_plot_waveform_density: passed != not found`
- `spiketools/tests/plts/test_spikes.py::test_plot_waveforms3d: passed != not found`
- `spiketools/tests/plts/test_stats.py::test_plot_surrogates: passed != not found`
- `spiketools/tests/plts/test_style.py::test_drop_spines: passed != not found`
- `spiketools/tests/plts/test_style.py::test_invert_axes: passed != not found`
- `spiketools/tests/plts/test_style.py::test_set_plt_kwargs: passed != not found`
- `spiketools/tests/plts/test_task.py::test_plot_task_events: passed != not found`
- `spiketools/tests/plts/test_task.py::test_plot_task_structure: passed != not found`
- `spiketools/tests/plts/test_trials.py::test_create_raster_title: passed != not found`
- `spiketools/tests/plts/test_trials.py::test_plot_raster_and_rates: passed != not found`
- `spiketools/tests/plts/test_trials.py::test_plot_rasters: passed != not found`
- `spiketools/tests/plts/test_trials.py::test_plot_rate_by_time: passed != not found`
- `spiketools/tests/plts/test_utils.py::test_check_ax: passed != not found`
- `spiketools/tests/plts/test_utils.py::test_get_attr_kwargs: passed != not found`
- `spiketools/tests/plts/test_utils.py::test_get_grid_subplot: passed != not found`
- `spiketools/tests/plts/test_utils.py::test_get_kwargs: passed != not found`
- `spiketools/tests/plts/test_utils.py::test_make_axes: passed != not found`
- `spiketools/tests/plts/test_utils.py::test_make_grid: passed != not found`
- `spiketools/tests/plts/test_utils.py::test_save_figure: passed != not found`
- `spiketools/tests/plts/test_utils.py::test_savefig: passed != not found`
- `spiketools/tests/sim/test_times.py::test_sim_spiketimes: passed != not found`
- `spiketools/tests/sim/test_times.py::test_sim_spiketimes_poisson: passed != not found`
- `spiketools/tests/sim/test_train.py::test_sim_spiketrain: passed != not found`
- `spiketools/tests/sim/test_train.py::test_sim_spiketrain_binom: passed != not found`
- `spiketools/tests/sim/test_train.py::test_sim_spiketrain_poisson: passed != not found`
- `spiketools/tests/sim/test_train.py::test_sim_spiketrain_prob: passed != not found`
- `spiketools/tests/sim/test_trials.py::test_sim_trials: passed != not found`
- `spiketools/tests/sim/test_trials.py::test_sim_trials_poisson: passed != not found`
- `spiketools/tests/sim/test_utils.py::test_apply_refractory_times: passed != not found`
- `spiketools/tests/sim/test_utils.py::test_apply_refractory_train: passed != not found`
- `spiketools/tests/sim/test_utils.py::test_refractory_times: passed != not found`
- `spiketools/tests/sim/test_utils.py::test_refractory_train: passed != not found`
- `spiketools/tests/spatial/test_checks.py::test_check_bin_definition: passed != not found`
- `spiketools/tests/spatial/test_checks.py::test_check_bin_widths: passed != not found`
- `spiketools/tests/spatial/test_checks.py::test_check_position: passed != not found`
- `spiketools/tests/spatial/test_distance.py::test_compute_cumulative_distances: passed != not found`
- `spiketools/tests/spatial/test_distance.py::test_compute_distance: passed != not found`
- `spiketools/tests/spatial/test_distance.py::test_compute_distances: passed != not found`
- `spiketools/tests/spatial/test_distance.py::test_compute_distances_to_location: passed != not found`
- `spiketools/tests/spatial/test_distance.py::test_get_closest_location: passed != not found`
- `spiketools/tests/spatial/test_information.py::test_compute_spatial_information: passed != not found`
- `spiketools/tests/spatial/test_occupancy.py::test_compute_bin_assignment: passed != not found`
- `spiketools/tests/spatial/test_occupancy.py::test_compute_bin_counts_assgn: passed != not found`
- `spiketools/tests/spatial/test_occupancy.py::test_compute_bin_counts_pos: passed != not found`
- `spiketools/tests/spatial/test_occupancy.py::test_compute_bin_edges: passed != not found`
- `spiketools/tests/spatial/test_occupancy.py::test_create_position_df: passed != not found`
- `spiketools/tests/spatial/test_occupancy.py::test_normalize_bin_counts: passed != not found`
- `spiketools/tests/spatial/test_place.py::test_compute_place_bins: passed != not found`
- `spiketools/tests/spatial/test_speed.py::test_compute_speed: passed != not found`
- `spiketools/tests/spatial/test_target.py::test_compute_target_bins: passed != not found`
- `spiketools/tests/spatial/test_utils.py::test_compute_bin_width: passed != not found`
- `spiketools/tests/spatial/test_utils.py::test_compute_nbins: passed != not found`
- `spiketools/tests/spatial/test_utils.py::test_compute_pos_ranges: passed != not found`
- `spiketools/tests/spatial/test_utils.py::test_convert_1dindices: passed != not found`
- `spiketools/tests/spatial/test_utils.py::test_convert_2dindices: passed != not found`
- `spiketools/tests/spatial/test_utils.py::test_get_position_xy: passed != not found`
- `spiketools/tests/stats/test_anova.py::test_create_dataframe: passed != not found`
- `spiketools/tests/stats/test_anova.py::test_create_dataframe_bins: passed != not found`
- `spiketools/tests/stats/test_generators.py::test_poisson_generator: passed != not found`
- `spiketools/tests/stats/test_permutations.py::test_compute_empirical_pvalue: passed != not found`
- `spiketools/tests/stats/test_permutations.py::test_compute_surrogate_stats: passed != not found`
- `spiketools/tests/stats/test_permutations.py::test_compute_surrogate_zscore: passed != not found`
- `spiketools/tests/stats/test_shuffle.py::test_drop_shuffle_range: passed != not found`
- `spiketools/tests/stats/test_shuffle.py::test_shuffle_bins: passed != not found`
- `spiketools/tests/stats/test_shuffle.py::test_shuffle_circular: passed != not found`
- `spiketools/tests/stats/test_shuffle.py::test_shuffle_isis: passed != not found`
- `spiketools/tests/stats/test_shuffle.py::test_shuffle_poisson: passed != not found`
- `spiketools/tests/stats/test_shuffle.py::test_shuffle_spikes: passed != not found`
- `spiketools/tests/stats/test_trials.py::test_compare_pre_post_activity: passed != not found`
- `spiketools/tests/stats/test_trials.py::test_compare_trial_frs: passed != not found`
- `spiketools/tests/stats/test_trials.py::test_compute_pre_post_ttest: passed != not found`
- `spiketools/tests/utils/test_base.py::test_add_key_prefix: passed != not found`
- `spiketools/tests/utils/test_base.py::test_check_keys: passed != not found`
- `spiketools/tests/utils/test_base.py::test_combine_dicts: passed != not found`
- `spiketools/tests/utils/test_base.py::test_count_elements: passed != not found`
- `spiketools/tests/utils/test_base.py::test_drop_key_prefix: passed != not found`
- `spiketools/tests/utils/test_base.py::test_flatten: passed != not found`
- `spiketools/tests/utils/test_base.py::test_listify: passed != not found`
- `spiketools/tests/utils/test_base.py::test_lower_list: passed != not found`
- `spiketools/tests/utils/test_base.py::test_relabel_keys: passed != not found`
- `spiketools/tests/utils/test_base.py::test_select_from_list: passed != not found`
- `spiketools/tests/utils/test_base.py::test_subset_dict: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_array_lst_orientation: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_array_orientation: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_axis: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_bin_range: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_list_options: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_param_lengths: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_param_options: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_param_range: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_param_type: passed != not found`
- `spiketools/tests/utils/test_checks.py::test_check_time_bins: passed != not found`
- `spiketools/tests/utils/test_data.py::test_assign_data_to_bins: passed != not found`
- `spiketools/tests/utils/test_data.py::test_compute_range: passed != not found`
- `spiketools/tests/utils/test_data.py::test_drop_nans: passed != not found`
- `spiketools/tests/utils/test_data.py::test_include_bin_edge: passed != not found`
- `spiketools/tests/utils/test_data.py::test_make_orientation: passed != not found`
- `spiketools/tests/utils/test_data.py::test_permute_vector: passed != not found`
- `spiketools/tests/utils/test_data.py::test_smooth_data: passed != not found`
- `spiketools/tests/utils/test_epoch.py::test_epoch_data_by_event: passed != not found`
- `spiketools/tests/utils/test_epoch.py::test_epoch_data_by_range: passed != not found`
- `spiketools/tests/utils/test_epoch.py::test_epoch_data_by_segment: passed != not found`
- `spiketools/tests/utils/test_epoch.py::test_epoch_data_by_time: passed != not found`
- `spiketools/tests/utils/test_epoch.py::test_epoch_spikes_by_event: passed != not found`
- `spiketools/tests/utils/test_epoch.py::test_epoch_spikes_by_range: passed != not found`
- `spiketools/tests/utils/test_epoch.py::test_epoch_spikes_by_segment: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_create_mask: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_create_nan_mask: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_drop_range: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_ind_by_time: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_ind_by_value: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_inds_by_times: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_inds_by_values: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_range: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_value_by_time: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_value_range: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_values_by_time_range: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_get_values_by_times: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_reinstate_range: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_reinstate_range_1d: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_select_from_arrays: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_threshold_spikes_by_times: passed != not found`
- `spiketools/tests/utils/test_extract.py::test_threshold_spikes_by_values: passed != not found`
- `spiketools/tests/utils/test_options.py::test_get_avg_func: passed != not found`
- `spiketools/tests/utils/test_options.py::test_get_comp_func: passed != not found`
- `spiketools/tests/utils/test_options.py::test_get_var_func: passed != not found`
- `spiketools/tests/utils/test_random.py::test_set_random_seed: passed != not found`
- `spiketools/tests/utils/test_random.py::test_set_random_state: passed != not found`
- `spiketools/tests/utils/test_run.py::test_create_methods_list: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_compute_sample_durations: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_convert_min_to_hour: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_convert_ms_to_min: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_convert_ms_to_sec: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_convert_nsamples_to_time: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_convert_sec_to_min: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_convert_time_to_nsamples: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_create_bin_times: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_format_time_string: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_infer_time_unit: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_split_time_value: passed != not found`
- `spiketools/tests/utils/test_timestamps.py::test_sum_time_ranges: passed != not found`
- `spiketools/tests/utils/test_trials.py::test_extract_conditions_dict: passed != not found`
- `spiketools/tests/utils/test_trials.py::test_recombine_trial_data: passed != not found`
- `spiketools/tests/utils/test_trials.py::test_split_trials_by_condition: passed != not found`
- `spiketools/tests/utils/test_trials.py::test_split_trials_by_condition_array: passed != not found`
- `spiketools/tests/utils/test_trials.py::test_split_trials_by_condition_list: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
- async_transform finished
