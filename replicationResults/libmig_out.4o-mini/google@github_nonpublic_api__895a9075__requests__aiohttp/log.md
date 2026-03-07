## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/google@github_nonpublic_api__895a9075__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 2, cov finished with status 1
## Running llmmig
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
- async_transform finished
## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/google@github_nonpublic_api__895a9075__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating github_nonpublic_api/api.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_api.py::TestApi::test_create_business_org: passed != failed`
- `tests/test_api.py::TestApi::test_create_personal_org: passed != failed`
- `tests/test_api.py::TestApi::test_download_usage_report: passed != failed`
- `tests/test_api.py::TestApi::test_get_and_submit_form: passed != failed`
- `tests/test_api.py::TestApi::test_get_and_submit_form_by_id: passed != failed`
- `tests/test_api.py::TestApi::test_get_and_submit_form_by_id_error: passed != failed`
- `tests/test_api.py::TestApi::test_install_app_on_org: passed != failed`
- `tests/test_api.py::TestApi::test_request_usage_report: passed != failed`
- `tests/test_api.py::TestApi::test_suspend_app_toggle: passed != failed`
- `tests/test_api.py::TestApi::test_update_app_permissions: passed != failed`
- `tests/test_api.py::TestApi::test_update_security_analysis_settings_code_scanning: passed != failed`
- `tests/test_api.py::TestApi::test_update_security_analysis_settings_code_scanning_3p: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 21 functions to mark async including 12 tests
- Found 20 calls to await
- 2 files requires transformation
- transforming tests/test_api.py
- transforming github_nonpublic_api/api.py
### running tests
- test finished with status 0, cov finished with status 0
- no test diff
### test diff with round premig
- async_transform finished
