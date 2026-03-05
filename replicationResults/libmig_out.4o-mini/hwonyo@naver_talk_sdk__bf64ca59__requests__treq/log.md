## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/hwonyo@naver_talk_sdk__bf64ca59__requests__treq/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating nta/api.py
### migrating nta/exceptions.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_connection_error_handle: passed != failed`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_handle_get_user_profile: passed != failed`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_handle_upload_image_url: passed != failed`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_with_detail_handle: passed != failed`
- `tests/api/test_message_product.py::TestNaverTalkAPI::test_send_text: passed != failed`
- `tests/api/test_persistent_menu.py::TestNaverTalkAPI::test_persistent_menu: passed != failed`
- `tests/api/test_persistent_menu.py::TestNaverTalkAPI::test_persistent_menu_with_None: passed != failed`
- `tests/api/test_request_profile.py::TestNaverTalkAPI::test_request_profile: passed != failed`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_composite_with_calendar: passed != failed`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_send_composite: passed != failed`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_send_composite_with_quick_reply: passed != failed`
- `tests/api/test_send_image.py::TestNaverTalkAPI::test_send_image: passed != failed`
- `tests/api/test_send_image.py::TestNaverTalkAPI::test_send_image_with_quick_reply: passed != failed`
- `tests/api/test_send_text.py::TestNaverTalkAPI::test_send_text: passed != failed`
- `tests/api/test_send_text.py::TestNaverTalkAPI::test_send_with_quick_reply: passed != failed`
- `tests/api/test_thread.py::TestNaverTalkAPI::test_thread_passing: passed != failed`
- `tests/api/test_thread.py::TestNaverTalkAPI::test_thread_taking: passed != failed`
- `tests/api/test_typing_action.py::TestNaverTalkActionEvent::test_typing_off: passed != failed`
- `tests/api/test_typing_action.py::TestNaverTalkActionEvent::test_typing_on: passed != failed`
- `tests/api/test_upload_image.py::TestNaverTalkAPI::test_upload_image: passed != failed`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_after_send: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
