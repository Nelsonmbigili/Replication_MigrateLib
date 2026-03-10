## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/giuliorossetti@ash__1106b609__matplotlib__plotly/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating ash_model/viz/static.py
### migrating ash_model/viz/temporal.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `ash_model/test/test_static_viz.py::StaticVizTestCase::test_plot_degree_distribution: passed != failed`
- `ash_model/test/test_static_viz.py::StaticVizTestCase::test_plot_hyperedge_size_distribution: passed != failed`
- `ash_model/test/test_static_viz.py::StaticVizTestCase::test_plot_s_degrees: passed != failed`
- `ash_model/test/test_static_viz.py::StaticVizTestCase::test_plot_s_ranks: passed != failed`
- `ash_model/test/test_temporal_viz.py::TemporalVizTestCase::test_plot_attribute_dynamics: passed != failed`
- `ash_model/test/test_temporal_viz.py::TemporalVizTestCase::test_plot_consistency: passed != failed`
- `ash_model/test/test_temporal_viz.py::TemporalVizTestCase::test_plot_structure_dynamics: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
