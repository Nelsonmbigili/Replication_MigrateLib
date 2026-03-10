## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/google@github_nonpublic_api__895a9075__requests__requests_futures/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating github_nonpublic_api/api.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_api.py::TestApi::test_create_business_org: passed != not found`
- `tests/test_api.py::TestApi::test_create_personal_org: passed != not found`
- `tests/test_api.py::TestApi::test_download_usage_report: passed != not found`
- `tests/test_api.py::TestApi::test_get_and_submit_form: passed != not found`
- `tests/test_api.py::TestApi::test_get_and_submit_form_by_id: passed != not found`
- `tests/test_api.py::TestApi::test_get_and_submit_form_by_id_error: passed != not found`
- `tests/test_api.py::TestApi::test_install_app_on_org: passed != not found`
- `tests/test_api.py::TestApi::test_request_usage_report: passed != not found`
- `tests/test_api.py::TestApi::test_suspend_app_toggle: passed != not found`
- `tests/test_api.py::TestApi::test_update_app_permissions: passed != not found`
- `tests/test_api.py::TestApi::test_update_security_analysis_settings_code_scanning: passed != not found`
- `tests/test_api.py::TestApi::test_update_security_analysis_settings_code_scanning_3p: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
