## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/coguardio@coguard-cli__48207839__requests__urllib3/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 4 files
### migrating src/coguard_cli/api_connection.py
### migrating src/coguard_cli/auth/token.py
### migrating src/coguard_cli/tests/auth/common_auth_function_test.py
### migrating src/coguard_cli/tests/auth/token_test.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_does_user_with_email_already_exist_200_status: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_does_user_with_email_already_exist_400_status: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_download_report_good_response_organization: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_download_report_good_response_user: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_get_fixable_rule_list_bad_response_ogranization: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_get_fixable_rule_list_bad_response_user_name: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_get_fixable_rule_list_ogranization: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_get_fixable_rule_list_user_name: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_get_latest_report_bad_response: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_get_latest_report_good_response_empty: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_get_latest_report_good_response_non_empty: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_log: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_log_with_error: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_mention_referrer_200_status: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_run_report: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_run_report_true: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_send_zip_file_for_fixing: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_send_zip_file_for_fixing_non_200_status: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_send_zip_file_for_scanning_200_status: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_send_zip_file_for_scanning_non_200_status: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_send_zip_file_for_scanning_with_org_204_failed_latest_report: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_send_zip_file_for_scanning_with_org_204_failed_run: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_send_zip_file_for_scanning_with_org_204_not_failed_latest_report: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_send_zip_file_for_scanning_with_org_non_204_status: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_sign_up_for_coguard_200_status: passed != failed`
- `src/coguard_cli/tests/api_connection_test.py::TestApiConnection::test_sign_up_for_coguard_400_status: passed != failed`
- `src/coguard_cli/tests/auth/token_test.py::TestTokenClass::test_authenticate_to_server_non_empty_config_object_404: passed != failed`
- `src/coguard_cli/tests/auth/token_test.py::TestTokenClass::test_authenticate_to_server_non_empty_config_object_success: passed != failed`
- `src/coguard_cli/tests/auth/token_test.py::TestTokenClass::test_get_public_key_status_200_no_public_key: passed != failed`
- `src/coguard_cli/tests/auth/token_test.py::TestTokenClass::test_get_public_key_status_200_public_key: passed != failed`
- `src/coguard_cli/tests/auth/token_test.py::TestTokenClass::test_get_public_key_status_not_200: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
