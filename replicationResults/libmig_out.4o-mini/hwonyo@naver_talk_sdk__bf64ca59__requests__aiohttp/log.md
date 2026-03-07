## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/hwonyo@naver_talk_sdk__bf64ca59__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating nta/api.py
### migrating nta/exceptions.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_callback_error: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_connection_error_handle: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_handle_get_user_profile: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_handle_upload_image_url: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_with_detail_handle: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_naver_pay: passed != not found`
- `tests/api/test_message_product.py::TestNaverTalkAPI::test_send_text: passed != not found`
- `tests/api/test_persistent_menu.py::TestNaverTalkAPI::test_persistent_menu: passed != not found`
- `tests/api/test_persistent_menu.py::TestNaverTalkAPI::test_persistent_menu_with_None: passed != not found`
- `tests/api/test_request_profile.py::TestNaverTalkAPI::test_request_profile: passed != not found`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_composite_with_calendar: passed != not found`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_send_composite: passed != not found`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_send_composite_with_quick_reply: passed != not found`
- `tests/api/test_send_image.py::TestNaverTalkAPI::test_send_image: passed != not found`
- `tests/api/test_send_image.py::TestNaverTalkAPI::test_send_image_with_quick_reply: passed != not found`
- `tests/api/test_send_text.py::TestNaverTalkAPI::test_send_text: passed != not found`
- `tests/api/test_send_text.py::TestNaverTalkAPI::test_send_with_quick_reply: passed != not found`
- `tests/api/test_thread.py::TestNaverTalkAPI::test_thread_passing: passed != not found`
- `tests/api/test_thread.py::TestNaverTalkAPI::test_thread_taking: passed != not found`
- `tests/api/test_typing_action.py::TestNaverTalkActionEvent::test_typing_off: passed != not found`
- `tests/api/test_typing_action.py::TestNaverTalkActionEvent::test_typing_on: passed != not found`
- `tests/api/test_upload_image.py::TestNaverTalkAPI::test_upload_image: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_after_send: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_before_proccess: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_callback: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_echo_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_friend_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_handover_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_leave_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_open_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_pay_complete_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_pay_confirm_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_profile_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_send_event_image: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_send_event_text: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_standby_true: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_unknown_event: passed != not found`
- `tests/models/test_base.py::TestBaseTemplate::test_convert_to_camel_case: passed != not found`
- `tests/models/test_base.py::TestBaseTemplate::test_dict_to_snake_case: passed != not found`
- `tests/models/test_base.py::TestBaseTemplate::test_new_from_json_dict: passed != not found`
- `tests/models/test_base.py::TestBaseTemplate::test_others: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_button_convert_test: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_button_nested: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_calendar_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_link_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_option_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_pay_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_text_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_time_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_time_interval: passed != not found`
- `tests/models/test_events.py::TestNaverTalkEvent::test_peresistent_menu_event: passed != not found`
- `tests/models/test_model_error_handle.py::TestNaverTalkApi::test_button_invalid_type_error: passed != not found`
- `tests/models/test_model_error_handle.py::TestNaverTalkApi::test_image_content_error: passed != not found`
- `tests/models/test_model_error_handle.py::TestNaverTalkApi::test_payload_error: passed != not found`
- `tests/models/test_payload.py::TestNaverTalkPayload::test_persistent_menu: passed != not found`
- `tests/models/test_payload.py::TestNaverTalkPayload::test_persistent_menu_with_None: passed != not found`
- `tests/models/test_payload.py::TestNaverTalkPayload::test_product_message: passed != not found`
- `tests/test_utils.py::TestUtils::test__byteify: passed != not found`
- `tests/test_utils.py::TestUtils::test_to_camel_case: passed != not found`
- `tests/test_utils.py::TestUtils::test_to_snake_case: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 31 functions to mark async including 23 tests
- Found 35 calls to await
- 12 files requires transformation
- transforming tests/api/test_error_handle.py
- transforming tests/api/test_message_product.py
- transforming tests/api/test_thread.py
- transforming tests/api/test_send_composite.py
- transforming tests/api/test_upload_image.py
- transforming tests/api/test_send_image.py
- transforming tests/api/test_persistent_menu.py
- transforming tests/api/test_request_profile.py
- transforming tests/api/test_typing_action.py
- transforming nta/api.py
- transforming tests/api/test_webhook_handler.py
- transforming tests/api/test_send_text.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_callback_error: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_connection_error_handle: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_handle_get_user_profile: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_handle_upload_image_url: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_error_with_detail_handle: passed != not found`
- `tests/api/test_error_handle.py::TestNaverTalkApi::test_naver_pay: passed != not found`
- `tests/api/test_message_product.py::TestNaverTalkAPI::test_send_text: passed != not found`
- `tests/api/test_persistent_menu.py::TestNaverTalkAPI::test_persistent_menu: passed != not found`
- `tests/api/test_persistent_menu.py::TestNaverTalkAPI::test_persistent_menu_with_None: passed != not found`
- `tests/api/test_request_profile.py::TestNaverTalkAPI::test_request_profile: passed != not found`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_composite_with_calendar: passed != not found`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_send_composite: passed != not found`
- `tests/api/test_send_composite.py::TestNaverTalkAPI::test_send_composite_with_quick_reply: passed != not found`
- `tests/api/test_send_image.py::TestNaverTalkAPI::test_send_image: passed != not found`
- `tests/api/test_send_image.py::TestNaverTalkAPI::test_send_image_with_quick_reply: passed != not found`
- `tests/api/test_send_text.py::TestNaverTalkAPI::test_send_text: passed != not found`
- `tests/api/test_send_text.py::TestNaverTalkAPI::test_send_with_quick_reply: passed != not found`
- `tests/api/test_thread.py::TestNaverTalkAPI::test_thread_passing: passed != not found`
- `tests/api/test_thread.py::TestNaverTalkAPI::test_thread_taking: passed != not found`
- `tests/api/test_typing_action.py::TestNaverTalkActionEvent::test_typing_off: passed != not found`
- `tests/api/test_typing_action.py::TestNaverTalkActionEvent::test_typing_on: passed != not found`
- `tests/api/test_upload_image.py::TestNaverTalkAPI::test_upload_image: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_after_send: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_before_proccess: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_callback: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_echo_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_friend_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_handover_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_leave_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_open_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_pay_complete_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_pay_confirm_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_profile_event: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_send_event_image: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_send_event_text: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_standby_true: passed != not found`
- `tests/api/test_webhook_handler.py::TestNaverTalkApi::test_unknown_event: passed != not found`
- `tests/models/test_base.py::TestBaseTemplate::test_convert_to_camel_case: passed != not found`
- `tests/models/test_base.py::TestBaseTemplate::test_dict_to_snake_case: passed != not found`
- `tests/models/test_base.py::TestBaseTemplate::test_new_from_json_dict: passed != not found`
- `tests/models/test_base.py::TestBaseTemplate::test_others: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_button_convert_test: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_button_nested: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_calendar_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_link_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_option_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_pay_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_text_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_time_button: passed != not found`
- `tests/models/test_buttons.py::TestNaverTalkApi::test_time_interval: passed != not found`
- `tests/models/test_events.py::TestNaverTalkEvent::test_peresistent_menu_event: passed != not found`
- `tests/models/test_model_error_handle.py::TestNaverTalkApi::test_button_invalid_type_error: passed != not found`
- `tests/models/test_model_error_handle.py::TestNaverTalkApi::test_image_content_error: passed != not found`
- `tests/models/test_model_error_handle.py::TestNaverTalkApi::test_payload_error: passed != not found`
- `tests/models/test_payload.py::TestNaverTalkPayload::test_persistent_menu: passed != not found`
- `tests/models/test_payload.py::TestNaverTalkPayload::test_persistent_menu_with_None: passed != not found`
- `tests/models/test_payload.py::TestNaverTalkPayload::test_product_message: passed != not found`
- `tests/test_utils.py::TestUtils::test__byteify: passed != not found`
- `tests/test_utils.py::TestUtils::test_to_camel_case: passed != not found`
- `tests/test_utils.py::TestUtils::test_to_snake_case: passed != not found`
- async_transform finished
