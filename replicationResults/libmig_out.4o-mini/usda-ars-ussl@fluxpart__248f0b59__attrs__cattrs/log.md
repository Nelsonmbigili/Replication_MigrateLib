## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/usda-ars-ussl@fluxpart__248f0b59__attrs__cattrs/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 3 files
### migrating fluxpart/containers.py
### migrating fluxpart/fluxpart.py
### migrating fluxpart/hfdata.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_partition.py::test_fvspart_interval: passed != not found`
- `tests/test_util.py::test_chunked_df: passed != not found`
- `tests/test_util.py::test_mulitifile_read_csv: passed != not found`
- `tests/test_util.py::test_read_warning: passed != not found`
- `tests/test_util.py::test_stats2: passed != not found`
- `tests/test_wue.py::test_water_use_efficiency: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
