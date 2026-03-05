## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/david96182@ninjemail__2a52a8cc__requests__urllib3/.venv
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
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `ninjemail/tests/test_email_gmail.py::test_create_account_chrome_and_fivesim: passed != not found`
- `ninjemail/tests/test_email_gmail.py::test_create_account_chrome_and_smspool: passed != not found`
- `ninjemail/tests/test_email_gmail.py::test_create_account_code_fail: passed != not found`
- `ninjemail/tests/test_email_gmail.py::test_create_account_firefox_and_getsmscode: passed != not found`
- `ninjemail/tests/test_email_gmail.py::test_create_account_phone_fail: passed != not found`
- `ninjemail/tests/test_email_outlook.py::test_create_account_chrome: passed != not found`
- `ninjemail/tests/test_email_outlook.py::test_create_account_firefox: passed != not found`
- `ninjemail/tests/test_email_outlook.py::test_create_hotmail_account: passed != not found`
- `ninjemail/tests/test_email_yahoo.py::test_create_account_chrome_and_smspool: passed != not found`
- `ninjemail/tests/test_email_yahoo.py::test_create_account_firefox_and_fivesim: passed != not found`
- `ninjemail/tests/test_email_yahoo.py::test_create_account_firefox_and_getsmscode: passed != not found`
- `ninjemail/tests/test_email_yahoo.py::test_create_myyahoo_account: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_gmail_account: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_gmail_account_no_info: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_gmail_account_no_sms_key: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_gmail_account_with_proxy: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_outlook_account: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_outlook_account_no_captcha_key: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_outlook_account_no_info: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_outlook_account_with_proxy: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_yahoo_account: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_yahoo_account_no_captcha_key: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_yahoo_account_no_info: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_yahoo_account_no_sms_key: passed != not found`
- `ninjemail/tests/test_manager.py::test_create_yahoo_account_with_proxy: passed != not found`
- `ninjemail/tests/test_manager.py::test_get_captcha_key_invalid_provider: passed != not found`
- `ninjemail/tests/test_manager.py::test_get_captcha_key_no_key_for_provider: passed != not found`
- `ninjemail/tests/test_manager.py::test_get_captcha_key_valid_provider: passed != not found`
- `ninjemail/tests/test_manager.py::test_get_proxy_with_auto_proxy_failure: passed != not found`
- `ninjemail/tests/test_manager.py::test_get_proxy_with_auto_proxy_success: passed != not found`
- `ninjemail/tests/test_manager.py::test_get_proxy_with_provided_proxy: passed != not found`
- `ninjemail/tests/test_manager.py::test_get_sms_key_no_keys: passed != not found`
- `ninjemail/tests/test_manager.py::test_get_sms_key_with_keys: passed != not found`
- `ninjemail/tests/test_manager.py::test_init_invalid_browser: passed != not found`
- `ninjemail/tests/test_manager.py::test_init_valid_browser: passed != not found`
- `ninjemail/tests/test_manager.py::test_init_valid_browser_undetected_chrome: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_get_code: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_get_code_error_response: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone_error_response: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_get_phone_with_prefix: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_no_free_phones: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_not_enough_balance: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_request_error_response: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_request_failure: passed != not found`
- `ninjemail/tests/test_sms_5sim.py::test_request_success: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_api_error_response_message: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_generate_generic: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_code: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_endpoint: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_phone: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_get_phone_with_prefix: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_initialization: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_no_code_found: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_request: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_request_failure: passed != not found`
- `ninjemail/tests/test_sms_getsmscode.py::test_request_timeout: passed != not found`
- `ninjemail/tests/test_sms_smspool.py::test_get_code: passed != not found`
- `ninjemail/tests/test_sms_smspool.py::test_get_code_error_response: passed != not found`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone: passed != not found`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone_error_response: passed != not found`
- `ninjemail/tests/test_sms_smspool.py::test_get_phone_with_prefix: passed != not found`
- `ninjemail/tests/test_sms_smspool.py::test_request_error_response: passed != not found`
- `ninjemail/tests/test_sms_smspool.py::test_request_failure: passed != not found`
- `ninjemail/tests/test_sms_smspool.py::test_request_success: passed != not found`
- `ninjemail/tests/test_utils.py::TestCountryProvider::test_country_returns_string: passed != not found`
- `ninjemail/tests/test_utils.py::TestGenerateMissingInfo::test_generate_all_missing: passed != not found`
- `ninjemail/tests/test_utils.py::TestGenerateMissingInfo::test_generate_partial_missing: passed != not found`
- `ninjemail/tests/test_utils.py::TestGenerateMissingInfo::test_uses_faker_for_generated_data: passed != not found`
- `ninjemail/tests/test_utils.py::TestGetBirthdate::test_birthdate_split_correctly: passed != not found`
- `ninjemail/tests/test_utils.py::TestGetBirthdate::test_birthdate_split_invalid_format: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_chrome_driver_no_proxy_no_captcha: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_chrome_driver_with_auth_proxy: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_chrome_driver_with_proxy: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_chrome_driver_with_proxy_and_capsolver: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_chrome_driver_with_proxy_and_nopecha: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_firefox_driver_no_proxy_no_captcha: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_firefox_driver_with_captcha_extension: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_firefox_driver_with_proxy: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_undetected_chrome_driver: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_undetected_chrome_driver_with_auth_proxy: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_undetected_chrome_driver_with_auth_proxy_and_nopecha: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_undetected_chrome_driver_with_proxy_and_capsolver: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_create_undetected_chrome_driver_with_proxy_and_nopecha: passed != not found`
- `ninjemail/tests/test_webdriver_utils.py::test_unsupported_browser: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
