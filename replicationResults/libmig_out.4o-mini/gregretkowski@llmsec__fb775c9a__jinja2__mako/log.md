## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/gregretkowski@llmsec__fb775c9a__jinja2__mako/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating llmsec/check_prompt.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_check_prompt.py::test_check_prompt_fails: passed != failed`
- `tests/test_check_prompt.py::test_check_prompt_oks: passed != failed`
- `tests/test_check_prompt.py::test_check_prompt_set_threshold: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
