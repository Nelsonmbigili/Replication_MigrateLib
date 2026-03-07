## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/cmccomb@trussme__0c7316cf__matplotlib__plotly/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating trussme/report.py
### migrating trussme/visualize.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_construction_and_io.py::TestSequenceFunctions::test_build_methods: passed != failed`
- `tests/test_construction_and_io.py::TestSequenceFunctions::test_demo_report: passed != failed`
- `tests/test_construction_and_io.py::TestSequenceFunctions::test_save_to_json_and_rebuild: passed != failed`
- `tests/test_construction_and_io.py::TestSequenceFunctions::test_save_to_trs_and_rebuild: passed != failed`
- `tests/test_optimization.py::TestCustomStuff::test_full_optimization: passed != failed`
- `tests/test_optimization.py::TestCustomStuff::test_joint_optimization: passed != failed`
- `tests/test_optimization.py::TestCustomStuff::test_setup: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
