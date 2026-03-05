## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/stephenhillier@starlette_exporter__05b9e18c__httpx__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating tests/test_middleware.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_middleware.py::TestAlwaysUseIntStatus::test_200_always_use_int_status_set: passed != failed`
- `tests/test_middleware.py::TestAlwaysUseIntStatus::test_200_with_always_use_int_status_set: passed != failed`
- `tests/test_middleware.py::TestBackgroundTasks::test_background_task_endpoint: passed != error`
- `tests/test_middleware.py::TestDefaultLabels::test_async_callable: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_callable_default_values: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_header: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_header_allowed_values: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_header_allowed_values_disallowed_value: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_allowed_values: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_allowed_values_disallowed: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_case_insensitive: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_default: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_http_exception: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_unhandled_exception: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_str_default_labels: passed != failed`
- `tests/test_middleware.py::TestExemplars::test_exemplar: passed != failed`
- `tests/test_middleware.py::TestExemplars::test_exemplar_request[False]: passed != failed`
- `tests/test_middleware.py::TestExemplars::test_exemplar_request[True]: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_200: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_404_filter: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_404_filter_unhandled_paths_off: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_404_group_unhandled_paths_on: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_500: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_app_name: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_histogram: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_histogram_custom_buckets: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_mounted_path: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_mounted_path_404: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_mounted_path_404_filter: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_mounted_path_with_param: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_multi_init: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_multi_prefix: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_prefix: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_requests_in_progress: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_skip_methods: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_skip_paths: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_skip_paths__re: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_skip_paths__re_partial: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_staticfiles_path: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_ungrouped_paths: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_unhandled: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_200: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_200_options: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_404: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_500: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_custom_root_path: passed != failed`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_histogram: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_mounted_path_404_filter: passed != failed`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_mounted_path_404_unfiltered: passed != failed`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_staticfiles_path: passed != failed`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_unhandled: passed != error`
- `tests/test_middleware.py::TestOptionalMetrics::test_receive_body_size: passed != error`
- `tests/test_middleware.py::TestOptionalMetrics::test_response_body_size: passed != error`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 59 functions to mark async including 52 tests
- Found 1 calls to await
- 2 files requires transformation
- transforming starlette_exporter/middleware.py
- transforming tests/test_middleware.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_middleware.py::TestAlwaysUseIntStatus::test_200_always_use_int_status_set: passed != failed`
- `tests/test_middleware.py::TestAlwaysUseIntStatus::test_200_with_always_use_int_status_set: passed != failed`
- `tests/test_middleware.py::TestBackgroundTasks::test_background_task_endpoint: passed != error`
- `tests/test_middleware.py::TestDefaultLabels::test_async_callable: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_callable_default_values: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_header: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_header_allowed_values: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_header_allowed_values_disallowed_value: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_allowed_values: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_allowed_values_disallowed: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_case_insensitive: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_default: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_http_exception: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_from_response_header_unhandled_exception: passed != failed`
- `tests/test_middleware.py::TestDefaultLabels::test_str_default_labels: passed != failed`
- `tests/test_middleware.py::TestExemplars::test_exemplar: passed != failed`
- `tests/test_middleware.py::TestExemplars::test_exemplar_request[False]: passed != failed`
- `tests/test_middleware.py::TestExemplars::test_exemplar_request[True]: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_200: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_404_filter: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_404_filter_unhandled_paths_off: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_404_group_unhandled_paths_on: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_500: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_app_name: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_histogram: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_histogram_custom_buckets: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_mounted_path: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_mounted_path_404: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_mounted_path_404_filter: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_mounted_path_with_param: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_multi_prefix: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_prefix: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_requests_in_progress: passed != error`
- `tests/test_middleware.py::TestMiddleware::test_skip_methods: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_skip_paths: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_skip_paths__re: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_skip_paths__re_partial: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_staticfiles_path: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_ungrouped_paths: passed != failed`
- `tests/test_middleware.py::TestMiddleware::test_unhandled: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_200: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_200_options: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_404: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_500: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_custom_root_path: passed != failed`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_histogram: passed != error`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_mounted_path_404_filter: passed != failed`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_mounted_path_404_unfiltered: passed != failed`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_staticfiles_path: passed != failed`
- `tests/test_middleware.py::TestMiddlewareGroupedPaths::test_unhandled: passed != error`
- `tests/test_middleware.py::TestOptionalMetrics::test_receive_body_size: passed != error`
- `tests/test_middleware.py::TestOptionalMetrics::test_response_body_size: passed != error`
- async_transform finished
