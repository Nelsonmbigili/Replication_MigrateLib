## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/apple@app-store-server-library-python__1202058d__httpx__urllib3/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating appstoreserverlibrary/api_client.py
### migrating tests/test_api_client_async.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_api_client.py::DecodedPayloads::test_api_error: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_api_too_many_requests: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_extend_renewal_date_for_all_active_subscribers: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_extend_subscription_renewal_date: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_all_subscription_statuses: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_notification_history: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_refund_history: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_status_of_subscription_renewal_date_extensions: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_test_notification_status: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_transaction_history_v1: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_transaction_history_v2: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_transaction_history_with_unknown_environment: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_get_transaction_info: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_look_up_order_id: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_request_test_notification: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_send_consumption_data: passed != failed`
- `tests/test_api_client.py::DecodedPayloads::test_unknown_error: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_api_error: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_api_too_many_requests: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_extend_renewal_date_for_all_active_subscribers: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_extend_subscription_renewal_date: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_all_subscription_statuses: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_notification_history: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_refund_history: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_status_of_subscription_renewal_date_extensions: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_test_notification_status: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_transaction_history_v1: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_transaction_history_v2: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_transaction_history_with_unknown_environment: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_get_transaction_info: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_look_up_order_id: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_request_test_notification: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_send_consumption_data: passed != failed`
- `tests/test_api_client_async.py::DecodedPayloads::test_unknown_error: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
