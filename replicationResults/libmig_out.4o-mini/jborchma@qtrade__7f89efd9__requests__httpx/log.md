## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/jborchma@qtrade__7f89efd9__requests__httpx/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating qtrade/questrade.py
### migrating tests/test_questrade.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_questrade.py::test_del_method_session_close: passed != failed`
- `tests/test_questrade.py::test_get_access_token: passed != failed`
- `tests/test_questrade.py::test_refresh_token_non_yaml: passed != failed`
- `tests/test_questrade.py::test_refresh_token_yaml: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
