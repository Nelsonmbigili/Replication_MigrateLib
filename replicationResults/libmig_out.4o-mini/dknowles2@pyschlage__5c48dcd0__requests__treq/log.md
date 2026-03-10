## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/dknowles2@pyschlage__5c48dcd0__requests__treq/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 3 files
### migrating pyschlage/auth.py
### migrating pyschlage/device.py
### migrating tests/test_auth.py
### running tests
- test finished with status 4, cov finished with status 1
### test diff with round premig
- `tests/test_api.py::test_locks: passed != not found`
- `tests/test_api.py::test_users: passed != not found`
- `tests/test_auth.py::test_authenticate: passed != not found`
- `tests/test_auth.py::test_request: passed != not found`
- `tests/test_auth.py::test_request_not_authorized: passed != not found`
- `tests/test_auth.py::test_request_unknown_error: passed != not found`
- `tests/test_auth.py::test_user_id: passed != not found`
- `tests/test_auth.py::test_user_id_is_cached: passed != not found`
- `tests/test_code.py::TestAccessCode::test_delete: passed != not found`
- `tests/test_code.py::TestAccessCode::test_save: passed != not found`
- `tests/test_code.py::TestAccessCode::test_to_from_json: passed != not found`
- `tests/test_code.py::TestAccessCode::test_to_from_json_recurring_schedule: passed != not found`
- `tests/test_common.py::test_pickle_unpickle: passed != not found`
- `tests/test_common.py::test_redact_all: passed != not found`
- `tests/test_common.py::test_redact_allow_all: passed != not found`
- `tests/test_common.py::test_redact_allow_asterisk: passed != not found`
- `tests/test_common.py::test_redact_partial: passed != not found`
- `tests/test_lock.py::TestChangedBy::test_keypad: passed != not found`
- `tests/test_lock.py::TestChangedBy::test_mobile_device: passed != not found`
- `tests/test_lock.py::TestChangedBy::test_nfc_device: passed != not found`
- `tests/test_lock.py::TestChangedBy::test_nfc_device_no_uuid: passed != not found`
- `tests/test_lock.py::TestChangedBy::test_no_metadata: passed != not found`
- `tests/test_lock.py::TestChangedBy::test_one_touch_locking: passed != not found`
- `tests/test_lock.py::TestChangedBy::test_thumbturn: passed != not found`
- `tests/test_lock.py::TestChangedBy::test_unknown: passed != not found`
- `tests/test_lock.py::TestKeypadDisabled::test_false: passed != not found`
- `tests/test_lock.py::TestKeypadDisabled::test_fetches_logs: passed != not found`
- `tests/test_lock.py::TestKeypadDisabled::test_fetches_logs_no_logs: passed != not found`
- `tests/test_lock.py::TestKeypadDisabled::test_true: passed != not found`
- `tests/test_lock.py::TestKeypadDisabled::test_true_unsorted: passed != not found`
- `tests/test_lock.py::TestLock::test_add_access_code: passed != not found`
- `tests/test_lock.py::TestLock::test_diagnostics: passed != not found`
- `tests/test_lock.py::TestLock::test_from_json: passed != not found`
- `tests/test_lock.py::TestLock::test_from_json_cat_optional: passed != not found`
- `tests/test_lock.py::TestLock::test_from_json_is_jammed: passed != not found`
- `tests/test_lock.py::TestLock::test_from_json_no_connected: passed != not found`
- `tests/test_lock.py::TestLock::test_from_json_no_model_name: passed != not found`
- `tests/test_lock.py::TestLock::test_from_json_wifi_lock_unavailable: passed != not found`
- `tests/test_lock.py::TestLock::test_lock_ble: passed != not found`
- `tests/test_lock.py::TestLock::test_lock_wifi: passed != not found`
- `tests/test_lock.py::TestLock::test_logs: passed != not found`
- `tests/test_lock.py::TestLock::test_refresh: passed != not found`
- `tests/test_lock.py::TestLock::test_refresh_access_codes: passed != not found`
- `tests/test_lock.py::TestLock::test_send_command_unauthenticated: passed != not found`
- `tests/test_lock.py::TestLock::test_set_auto_lock_time: passed != not found`
- `tests/test_lock.py::TestLock::test_set_beeper: passed != not found`
- `tests/test_lock.py::TestLock::test_set_lock_and_leave: passed != not found`
- `tests/test_lock.py::TestLock::test_unlock_ble: passed != not found`
- `tests/test_lock.py::TestLock::test_unlock_wifi: passed != not found`
- `tests/test_notification.py::test_delete: passed != not found`
- `tests/test_notification.py::test_from_json: passed != not found`
- `tests/test_notification.py::test_save: passed != not found`
- `tests/test_user.py::test_from_json: passed != not found`
- `tests/test_user.py::test_from_json_no_name: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
