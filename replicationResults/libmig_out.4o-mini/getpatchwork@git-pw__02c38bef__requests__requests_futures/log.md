## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/getpatchwork@git-pw__02c38bef__requests__requests_futures/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating git_pw/api.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_api.py::test_get_project_undefined: passed != not found`
- `tests/test_api.py::test_get_project_wildcard: passed != not found`
- `tests/test_api.py::test_get_server_missing_version: passed != not found`
- `tests/test_api.py::test_get_server_missing_version_and_path: passed != not found`
- `tests/test_api.py::test_get_server_undefined: passed != not found`
- `tests/test_api.py::test_retrieve_filter_ids: passed != not found`
- `tests/test_api.py::test_retrieve_filter_ids_multiple_matches_1_0: passed != not found`
- `tests/test_api.py::test_retrieve_filter_ids_multiple_matches_1_1: passed != not found`
- `tests/test_api.py::test_retrieve_filter_ids_no_matches: passed != not found`
- `tests/test_api.py::test_retrieve_filter_ids_too_short: passed != not found`
- `tests/test_api.py::test_version: passed != not found`
- `tests/test_api.py::test_version_missing: passed != not found`
- `tests/test_bundle.py::AddTestCase::test_add: passed != not found`
- `tests/test_bundle.py::AddTestCase::test_add_api_v1_1: passed != not found`
- `tests/test_bundle.py::ApplyTestCase::test_apply_with_args: passed != not found`
- `tests/test_bundle.py::ApplyTestCase::test_apply_without_args: passed != not found`
- `tests/test_bundle.py::CreateTestCase::test_create: passed != not found`
- `tests/test_bundle.py::CreateTestCase::test_create_api_v1_1: passed != not found`
- `tests/test_bundle.py::CreateTestCase::test_create_with_public: passed != not found`
- `tests/test_bundle.py::DeleteTestCase::test_delete: passed != not found`
- `tests/test_bundle.py::DeleteTestCase::test_delete_api_v1_1: passed != not found`
- `tests/test_bundle.py::DownloadTestCase::test_download: passed != not found`
- `tests/test_bundle.py::DownloadTestCase::test_download_to_file: passed != not found`
- `tests/test_bundle.py::GetBundleTestCase::test_get_by_id: passed != not found`
- `tests/test_bundle.py::GetBundleTestCase::test_get_by_name: passed != not found`
- `tests/test_bundle.py::GetBundleTestCase::test_get_by_name_too_few_matches: passed != not found`
- `tests/test_bundle.py::GetBundleTestCase::test_get_by_name_too_many_matches: passed != not found`
- `tests/test_bundle.py::ListTestCase::test_list: passed != not found`
- `tests/test_bundle.py::ListTestCase::test_list_api_v1_1: passed != not found`
- `tests/test_bundle.py::ListTestCase::test_list_with_filters: passed != not found`
- `tests/test_bundle.py::ListTestCase::test_list_with_formatting: passed != not found`
- `tests/test_bundle.py::ListTestCase::test_list_with_multiple_filters: passed != not found`
- `tests/test_bundle.py::ListTestCase::test_list_with_wildcard_filters: passed != not found`
- `tests/test_bundle.py::RemoveTestCase::test_remove: passed != not found`
- `tests/test_bundle.py::RemoveTestCase::test_remove_api_v1_1: passed != not found`
- `tests/test_bundle.py::RemoveTestCase::test_remove_empty: passed != not found`
- `tests/test_bundle.py::ShowTestCase::test_show: passed != not found`
- `tests/test_bundle.py::UpdateTestCase::test_update: passed != not found`
- `tests/test_bundle.py::UpdateTestCase::test_update_api_v1_1: passed != not found`
- `tests/test_bundle.py::UpdateTestCase::test_update_with_public: passed != not found`
- `tests/test_patch.py::ApplyTestCase::test_apply: passed != not found`
- `tests/test_patch.py::ApplyTestCase::test_apply_with_args: passed != not found`
- `tests/test_patch.py::ApplyTestCase::test_apply_with_series: passed != not found`
- `tests/test_patch.py::ApplyTestCase::test_apply_without_deps: passed != not found`
- `tests/test_patch.py::DownloadTestCase::test_download: passed != not found`
- `tests/test_patch.py::DownloadTestCase::test_download_diff: passed != not found`
- `tests/test_patch.py::DownloadTestCase::test_download_diff_to_file: passed != not found`
- `tests/test_patch.py::DownloadTestCase::test_download_to_file: passed != not found`
- `tests/test_patch.py::ListTestCase::test_list: passed != not found`
- `tests/test_patch.py::ListTestCase::test_list_api_v1_1: passed != not found`
- `tests/test_patch.py::ListTestCase::test_list_with_filters: passed != not found`
- `tests/test_patch.py::ListTestCase::test_list_with_formatting: passed != not found`
- `tests/test_patch.py::ListTestCase::test_list_with_multiple_filters: passed != not found`
- `tests/test_patch.py::ListTestCase::test_list_with_wildcard_filters: passed != not found`
- `tests/test_patch.py::ShowTestCase::test_show: passed != not found`
- `tests/test_patch.py::UpdateTestCase::test_update_no_arguments: passed != not found`
- `tests/test_patch.py::UpdateTestCase::test_update_with_arguments: passed != not found`
- `tests/test_patch.py::UpdateTestCase::test_update_with_delegate: passed != not found`
- `tests/test_patch.py::UpdateTestCase::test_update_with_invalid_state: passed != not found`
- `tests/test_series.py::ApplyTestCase::test_apply_with_args: passed != not found`
- `tests/test_series.py::ApplyTestCase::test_apply_without_args: passed != not found`
- `tests/test_series.py::DownloadTestCase::test_download: passed != not found`
- `tests/test_series.py::DownloadTestCase::test_download_separate_to_dir: passed != not found`
- `tests/test_series.py::DownloadTestCase::test_download_to_file: passed != not found`
- `tests/test_series.py::ListTestCase::test_list: passed != not found`
- `tests/test_series.py::ListTestCase::test_list_api_v1_1: passed != not found`
- `tests/test_series.py::ListTestCase::test_list_with_filters: passed != not found`
- `tests/test_series.py::ListTestCase::test_list_with_formatting: passed != not found`
- `tests/test_series.py::ListTestCase::test_list_with_multiple_filters: passed != not found`
- `tests/test_series.py::ListTestCase::test_list_with_wildcard_filters: passed != not found`
- `tests/test_series.py::ShowTestCase::test_show: passed != not found`
- `tests/test_utils.py::test_echo_via_pager_config: passed != not found`
- `tests/test_utils.py::test_echo_via_pager_env_GIT_PAGER: passed != not found`
- `tests/test_utils.py::test_echo_via_pager_env_PAGER: passed != not found`
- `tests/test_utils.py::test_echo_via_pager_env_default: passed != not found`
- `tests/test_utils.py::test_git_config: passed != not found`
- `tests/test_utils.py::test_git_config_error: passed != not found`
- `tests/test_utils.py::test_git_config_unicode: passed != not found`
- `tests/test_utils.py::test_tabulate_csv: passed != not found`
- `tests/test_utils.py::test_tabulate_default: passed != not found`
- `tests/test_utils.py::test_tabulate_git_config: passed != not found`
- `tests/test_utils.py::test_tabulate_simple: passed != not found`
- `tests/test_utils.py::test_tabulate_table: passed != not found`
- `tests/test_utils.py::test_tabulate_yaml: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
