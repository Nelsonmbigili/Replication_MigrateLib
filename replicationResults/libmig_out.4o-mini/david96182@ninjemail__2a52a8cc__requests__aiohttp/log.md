## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/david96182@ninjemail__2a52a8cc__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 6 files
### migrating ninjemail/sms_services/fivesim.py
### migrating ninjemail/sms_services/getsmscode.py
### migrating ninjemail/sms_services/smspool.py
### migrating ninjemail/tests/test_sms_5sim.py
### migrating ninjemail/tests/test_sms_getsmscode.py
### migrating ninjemail/tests/test_sms_smspool.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `ninjemail/tests/test_email_gmail.py::test_create_account_chrome_and_smspool: passed != failed`
- `ninjemail/tests/test_email_gmail.py::test_create_account_code_fail: passed != failed`
- `ninjemail/tests/test_email_yahoo.py::test_create_account_chrome_and_smspool: passed != failed`
- `ninjemail/tests/test_email_yahoo.py::test_create_myyahoo_account: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_code: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_code_error_response: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone_error_response: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone_with_prefix: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_no_free_phones: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_not_enough_balance: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_response: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_failure: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_success: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_api_error_response_message: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_code: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_phone: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_phone_with_prefix: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_no_code_found: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_request: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_request_failure: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_request_timeout: passed != failed`
- `ninjemail/tests/test_sms_smspool.py::test_get_code: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_get_code_error_response: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone_error_response: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone_with_prefix: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_request_error_response: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_request_failure: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_request_success: passed != error`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 35 functions to mark async including 26 tests
- Found 32 calls to await
- 6 files requires transformation
- transforming ninjemail/sms_services/getsmscode.py
- transforming ninjemail/tests/test_sms_5sim.py
- transforming ninjemail/tests/test_sms_smspool.py
- transforming ninjemail/sms_services/smspool.py
- transforming ninjemail/tests/test_sms_getsmscode.py
- transforming ninjemail/sms_services/fivesim.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `ninjemail/tests/test_email_gmail.py::test_create_account_chrome_and_smspool: passed != failed`
- `ninjemail/tests/test_email_gmail.py::test_create_account_code_fail: passed != failed`
- `ninjemail/tests/test_email_yahoo.py::test_create_account_chrome_and_smspool: passed != failed`
- `ninjemail/tests/test_email_yahoo.py::test_create_myyahoo_account: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_code: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_code_error_response: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone_error_response: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone_with_prefix: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_no_free_phones: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_not_enough_balance: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_response: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_failure: passed != failed`
- `ninjemail/tests/test_sms_5sim.py::test_request_success: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_api_error_response_message: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_code: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_phone: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_phone_with_prefix: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_no_code_found: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_request: passed != failed`
- `ninjemail/tests/test_sms_getsmscode.py::test_request_timeout: passed != failed`
- `ninjemail/tests/test_sms_smspool.py::test_get_code: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_get_code_error_response: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone_error_response: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone_with_prefix: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_request_error_response: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_request_failure: passed != error`
- `ninjemail/tests/test_sms_smspool.py::test_request_success: passed != error`
- async_transform finished
