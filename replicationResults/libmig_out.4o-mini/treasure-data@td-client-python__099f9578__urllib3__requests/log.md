## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/treasure-data@td-client-python__099f9578__urllib3__requests/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 3 files
### migrating tdclient/api.py
### migrating tdclient/test/api_test.py
### migrating tdclient/test/conftest.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tdclient/test/api_test.py::test_default_endpoint: passed != failed`
- `tdclient/test/api_test.py::test_delete_error: passed != failed`
- `tdclient/test/api_test.py::test_delete_failure: passed != failed`
- `tdclient/test/api_test.py::test_delete_retry_success: passed != failed`
- `tdclient/test/api_test.py::test_delete_success: passed != failed`
- `tdclient/test/api_test.py::test_delete_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_endpoint_from_environ: passed != failed`
- `tdclient/test/api_test.py::test_endpoint_from_keyword: passed != failed`
- `tdclient/test/api_test.py::test_endpoint_prefer_keyword: passed != failed`
- `tdclient/test/api_test.py::test_get_error: passed != failed`
- `tdclient/test/api_test.py::test_get_failure: passed != failed`
- `tdclient/test/api_test.py::test_get_retry_success: passed != failed`
- `tdclient/test/api_test.py::test_get_success: passed != failed`
- `tdclient/test/api_test.py::test_get_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_http_endpoint_with_custom_port: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_from_environ: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_from_keyword: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_prefer_keyword: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_with_credentials: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_with_scheme: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_with_scheme_and_credentials: passed != failed`
- `tdclient/test/api_test.py::test_https_endpoint: passed != failed`
- `tdclient/test/api_test.py::test_https_endpoint_with_custom_path: passed != failed`
- `tdclient/test/api_test.py::test_no_timeout: passed != failed`
- `tdclient/test/api_test.py::test_post_bytearray_success: passed != failed`
- `tdclient/test/api_test.py::test_post_failure: passed != failed`
- `tdclient/test/api_test.py::test_post_never_retry: passed != failed`
- `tdclient/test/api_test.py::test_post_retry_success: passed != failed`
- `tdclient/test/api_test.py::test_post_success: passed != failed`
- `tdclient/test/api_test.py::test_post_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_put_bytes_success: passed != failed`
- `tdclient/test/api_test.py::test_put_bytes_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_put_failure: passed != failed`
- `tdclient/test/api_test.py::test_put_file_with_fileno_success: passed != failed`
- `tdclient/test/api_test.py::test_put_file_with_fileno_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_put_file_without_fileno_success: passed != failed`
- `tdclient/test/api_test.py::test_put_file_without_fileno_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_raise_error_401: passed != failed`
- `tdclient/test/api_test.py::test_raise_error_403: passed != failed`
- `tdclient/test/api_test.py::test_raise_error_404: passed != failed`
- `tdclient/test/api_test.py::test_raise_error_409: passed != failed`
- `tdclient/test/api_test.py::test_timeout: passed != failed`
- `tdclient/test/bulk_import_api_test.py::test_list_bulk_imports_failure: passed != failed`
- `tdclient/test/database_api_test.py::test_list_databases_failure: passed != failed`
- `tdclient/test/export_api_test.py::test_export_data_failure: passed != failed`
- `tdclient/test/import_api_test.py::test_import_data_failure: passed != failed`
- `tdclient/test/job_api_test.py::test_list_jobs_failure: passed != failed`
- `tdclient/test/partial_delete_api_test.py::test_partial_delete_failure: passed != failed`
- `tdclient/test/result_api_test.py::test_list_result_failure: passed != failed`
- `tdclient/test/schedule_api_test.py::test_list_schedules_failure: passed != failed`
- `tdclient/test/table_api_test.py::test_list_tables_failure: passed != failed`
- `tdclient/test/user_api_test.py::test_list_users_failure: passed != failed`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tdclient/test/api_test.py::test_default_endpoint: passed != failed`
- `tdclient/test/api_test.py::test_delete_error: passed != failed`
- `tdclient/test/api_test.py::test_delete_failure: passed != failed`
- `tdclient/test/api_test.py::test_delete_retry_success: passed != failed`
- `tdclient/test/api_test.py::test_delete_success: passed != failed`
- `tdclient/test/api_test.py::test_delete_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_endpoint_from_environ: passed != failed`
- `tdclient/test/api_test.py::test_endpoint_from_keyword: passed != failed`
- `tdclient/test/api_test.py::test_endpoint_prefer_keyword: passed != failed`
- `tdclient/test/api_test.py::test_get_error: passed != failed`
- `tdclient/test/api_test.py::test_get_failure: passed != failed`
- `tdclient/test/api_test.py::test_get_retry_success: passed != failed`
- `tdclient/test/api_test.py::test_get_success: passed != failed`
- `tdclient/test/api_test.py::test_get_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_http_endpoint_with_custom_port: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_from_environ: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_from_keyword: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_prefer_keyword: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_with_credentials: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_with_scheme: passed != failed`
- `tdclient/test/api_test.py::test_http_proxy_with_scheme_and_credentials: passed != failed`
- `tdclient/test/api_test.py::test_https_endpoint: passed != failed`
- `tdclient/test/api_test.py::test_https_endpoint_with_custom_path: passed != failed`
- `tdclient/test/api_test.py::test_no_timeout: passed != failed`
- `tdclient/test/api_test.py::test_post_bytearray_success: passed != failed`
- `tdclient/test/api_test.py::test_post_failure: passed != failed`
- `tdclient/test/api_test.py::test_post_never_retry: passed != failed`
- `tdclient/test/api_test.py::test_post_retry_success: passed != failed`
- `tdclient/test/api_test.py::test_post_success: passed != failed`
- `tdclient/test/api_test.py::test_post_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_put_bytes_success: passed != failed`
- `tdclient/test/api_test.py::test_put_bytes_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_put_failure: passed != failed`
- `tdclient/test/api_test.py::test_put_file_with_fileno_success: passed != failed`
- `tdclient/test/api_test.py::test_put_file_with_fileno_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_put_file_without_fileno_success: passed != failed`
- `tdclient/test/api_test.py::test_put_file_without_fileno_unicode_success: passed != failed`
- `tdclient/test/api_test.py::test_raise_error_401: passed != failed`
- `tdclient/test/api_test.py::test_raise_error_403: passed != failed`
- `tdclient/test/api_test.py::test_raise_error_404: passed != failed`
- `tdclient/test/api_test.py::test_raise_error_409: passed != failed`
- `tdclient/test/api_test.py::test_timeout: passed != failed`
- `tdclient/test/bulk_import_api_test.py::test_list_bulk_imports_failure: passed != failed`
- `tdclient/test/database_api_test.py::test_list_databases_failure: passed != failed`
- `tdclient/test/export_api_test.py::test_export_data_failure: passed != failed`
- `tdclient/test/import_api_test.py::test_import_data_failure: passed != failed`
- `tdclient/test/job_api_test.py::test_list_jobs_failure: passed != failed`
- `tdclient/test/partial_delete_api_test.py::test_partial_delete_failure: passed != failed`
- `tdclient/test/result_api_test.py::test_list_result_failure: passed != failed`
- `tdclient/test/schedule_api_test.py::test_list_schedules_failure: passed != failed`
- `tdclient/test/table_api_test.py::test_list_tables_failure: passed != failed`
- `tdclient/test/user_api_test.py::test_list_users_failure: passed != failed`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
