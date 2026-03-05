## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/spiketools@spiketools__3df1ec3a__matplotlib__seaborn/.venv
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
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `spiketools/tests/plts/test_annotate.py::test_add_box_shade: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_box_shades: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_dots: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_gridlines: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_hlines: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_hshades: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_significance: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_text_labels_x: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_text_labels_y: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_vlines: passed != failed`
- `spiketools/tests/plts/test_annotate.py::test_add_vshades: passed != failed`
- `spiketools/tests/plts/test_data.py::test_plot_bar: passed != failed`
- `spiketools/tests/plts/test_data.py::test_plot_barh: passed != failed`
- `spiketools/tests/plts/test_data.py::test_plot_hist: passed != failed`
- `spiketools/tests/plts/test_data.py::test_plot_lines: passed != failed`
- `spiketools/tests/plts/test_data.py::test_plot_points: passed != failed`
- `spiketools/tests/plts/test_data.py::test_plot_polar_hist: passed != failed`
- `spiketools/tests/plts/test_data.py::test_plot_scatter: passed != failed`
- `spiketools/tests/plts/test_spatial.py::test_plot_heatmap: passed != failed`
- `spiketools/tests/plts/test_spatial.py::test_plot_position_1d: passed != failed`
- `spiketools/tests/plts/test_spatial.py::test_plot_position_by_time: passed != failed`
- `spiketools/tests/plts/test_spatial.py::test_plot_positions: passed != failed`
- `spiketools/tests/plts/test_spatial.py::test_plot_trial_heatmaps: passed != failed`
- `spiketools/tests/plts/test_spikes.py::test_plot_firing_rates: passed != failed`
- `spiketools/tests/plts/test_spikes.py::test_plot_isis: passed != failed`
- `spiketools/tests/plts/test_spikes.py::test_plot_waveform: passed != failed`
- `spiketools/tests/plts/test_spikes.py::test_plot_waveform_density: passed != failed`
- `spiketools/tests/plts/test_spikes.py::test_plot_waveforms3d: passed != failed`
- `spiketools/tests/plts/test_stats.py::test_plot_surrogates: passed != failed`
- `spiketools/tests/plts/test_style.py::test_drop_spines: passed != failed`
- `spiketools/tests/plts/test_style.py::test_invert_axes: passed != failed`
- `spiketools/tests/plts/test_style.py::test_set_plt_kwargs: passed != failed`
- `spiketools/tests/plts/test_task.py::test_plot_task_events: passed != failed`
- `spiketools/tests/plts/test_task.py::test_plot_task_structure: passed != failed`
- `spiketools/tests/plts/test_trials.py::test_plot_raster_and_rates: passed != failed`
- `spiketools/tests/plts/test_trials.py::test_plot_rasters: passed != failed`
- `spiketools/tests/plts/test_trials.py::test_plot_rate_by_time: passed != failed`
- `spiketools/tests/plts/test_utils.py::test_check_ax: passed != failed`
- `spiketools/tests/plts/test_utils.py::test_get_grid_subplot: passed != failed`
- `spiketools/tests/plts/test_utils.py::test_make_axes: passed != failed`
- `spiketools/tests/plts/test_utils.py::test_make_grid: passed != failed`
- `spiketools/tests/plts/test_utils.py::test_save_figure: passed != failed`
- `spiketools/tests/plts/test_utils.py::test_savefig: passed != failed`
- `spiketools/tests/stats/test_permutations.py::test_compute_surrogate_stats: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
