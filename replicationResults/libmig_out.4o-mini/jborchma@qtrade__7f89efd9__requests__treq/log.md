## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/jborchma@qtrade__7f89efd9__requests__treq/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating qtrade/questrade.py
### migrating tests/test_questrade.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_questrade.py::test_del_method_session_close: passed != not found`
- `tests/test_questrade.py::test_get_access_token: passed != not found`
- `tests/test_questrade.py::test_get_account_id: passed != not found`
- `tests/test_questrade.py::test_get_activity: passed != not found`
- `tests/test_questrade.py::test_get_balances: passed != not found`
- `tests/test_questrade.py::test_get_execution: passed != not found`
- `tests/test_questrade.py::test_get_historical_data: passed != not found`
- `tests/test_questrade.py::test_get_option_chain: passed != not found`
- `tests/test_questrade.py::test_get_positions: passed != not found`
- `tests/test_questrade.py::test_get_quote: passed != not found`
- `tests/test_questrade.py::test_get_ticker_information: passed != not found`
- `tests/test_questrade.py::test_init_via_incomplete_yaml: passed != not found`
- `tests/test_questrade.py::test_init_via_yaml: passed != not found`
- `tests/test_questrade.py::test_refresh_token_non_yaml: passed != not found`
- `tests/test_questrade.py::test_refresh_token_yaml: passed != not found`
- `tests/test_utility.py::test_get_access_token_error: passed != not found`
- `tests/test_utility.py::test_get_access_token_yaml: passed != not found`
- `tests/test_utility.py::test_get_access_token_yaml_error: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
