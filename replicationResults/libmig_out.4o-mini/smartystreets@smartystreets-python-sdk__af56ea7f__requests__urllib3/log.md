## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/smartystreets@smartystreets-python-sdk__af56ea7f__requests__urllib3/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating smartystreets_python_sdk/custom_header_sender.py
### migrating smartystreets_python_sdk/requests_sender.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test/custom_header_test.py::TestCustomHeaderSender::test_custom_headers_set: passed != not found`
- `test/custom_header_test.py::TestCustomHeaderSender::test_custom_headers_used: passed != not found`
- `test/custom_header_test.py::TestCustomHeaderSender::test_populates_headers: passed != not found`
- `test/international_autocomplete/candidate_test.py::TestSuggestion::test_all_fields_get_filled_in_correctly: passed != not found`
- `test/international_autocomplete/client_test.py::TestClient::test_deserialize_called_with_response_body: passed != not found`
- `test/international_autocomplete/client_test.py::TestClient::test_raises_exception_when_response_has_error: passed != not found`
- `test/international_autocomplete/client_test.py::TestClient::test_rejects_blank_lookup: passed != not found`
- `test/international_autocomplete/client_test.py::TestClient::test_result_correctly_assigned_to_corresponding_lookup: passed != not found`
- `test/international_autocomplete/client_test.py::TestClient::test_sending_fully_populated_lookup: passed != not found`
- `test/international_autocomplete/client_test.py::TestClient::test_sending_prefix_only_lookup: passed != not found`
- `test/international_street/candidate_test.py::TestCandidate::test_all_fields_filled_correctly: passed != not found`
- `test/international_street/client_test.py::TestClient::test_accepts_lookups_with_enough_info: passed != not found`
- `test/international_street/client_test.py::TestClient::test_candidates_correctly_assigned_to_lookup: passed != not found`
- `test/international_street/client_test.py::TestClient::test_deserialize_called_with_response_body: passed != not found`
- `test/international_street/client_test.py::TestClient::test_empty_lookup_rejected: passed != not found`
- `test/international_street/client_test.py::TestClient::test_rejects_lookups_with_only_country: passed != not found`
- `test/international_street/client_test.py::TestClient::test_rejects_lookups_with_only_country_and_address1: passed != not found`
- `test/international_street/client_test.py::TestClient::test_rejects_lookups_with_only_country_and_address1_and_administrative_area: passed != not found`
- `test/international_street/client_test.py::TestClient::test_rejects_lookups_with_only_country_and_address1_and_locality: passed != not found`
- `test/international_street/client_test.py::TestClient::test_sending_freeform_lookup: passed != not found`
- `test/international_street/client_test.py::TestClient::test_sending_single_fully_populated_lookup: passed != not found`
- `test/license_test.py::TestLicenseSender::test_license_not_set: passed != not found`
- `test/license_test.py::TestLicenseSender::test_license_set: passed != not found`
- `test/requests_sender_test.py::TestRequestsSender::test_http_request_contains_post_when_appropriate: passed != not found`
- `test/requests_sender_test.py::TestRequestsSender::test_request_contains_correct_content: passed != not found`
- `test/requests_sender_test.py::TestRequestsSender::test_request_has_correct_content_type: passed != not found`
- `test/requests_sender_test.py::TestRequestsSender::test_smartyresponse_contains_correct_payload: passed != not found`
- `test/requests_sender_test.py::TestRequestsSender::test_smartyresponse_contains_status_code_200_on_success: passed != not found`
- `test/requests_sender_test.py::TestRequestsSender::test_smartyresponse_contains_status_code_400_when_server_gives_a_400: passed != not found`
- `test/retry_sender_test.py::TestRetrySender::test_backoff_does_not_exceed_max: passed != not found`
- `test/retry_sender_test.py::TestRetrySender::test_payment_required_does_not_retry: passed != not found`
- `test/retry_sender_test.py::TestRetrySender::test_retry_until_success: passed != not found`
- `test/retry_sender_test.py::TestRetrySender::test_return_response_if_retry_limit_exceeded: passed != not found`
- `test/retry_sender_test.py::TestRetrySender::test_sleep_on_rate_limit: passed != not found`
- `test/retry_sender_test.py::TestRetrySender::test_sleep_on_rate_limit_error: passed != not found`
- `test/retry_sender_test.py::TestRetrySender::test_success_does_not_retry: passed != not found`
- `test/standard_serializer_test.py::TestStandardSerializer::test_deserialize: passed != not found`
- `test/standard_serializer_test.py::TestStandardSerializer::test_serialize: passed != not found`
- `test/url_prefix_sender_test.py::TestURLPrefixSender::test_multiple_sends: passed != not found`
- `test/url_prefix_sender_test.py::TestURLPrefixSender::test_request_url_not_present: passed != not found`
- `test/url_prefix_sender_test.py::TestURLPrefixSender::test_request_url_present: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_Financial_Lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_Financial_address_Lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_geo_reference_address_lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_geo_reference_lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_principal_address_lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_principal_lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_secondary_address_lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_secondary_count_address_lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_secondary_count_lookup: passed != not found`
- `test/us_enrichment/client_test.py::TestClient::test_sending_secondary_lookup: passed != not found`
- `test/us_enrichment/result_test.py::ResultTest::test_result_generic_deserialization: passed != not found`
- `test/us_extract/client_test.py::TestClient::test_content_type_set_correctly: passed != not found`
- `test/us_extract/client_test.py::TestClient::test_deserialize_called_with_response_body: passed != not found`
- `test/us_extract/client_test.py::TestClient::test_raises_exception_when_response_has_error: passed != not found`
- `test/us_extract/client_test.py::TestClient::test_reject_blank_lookup: passed != not found`
- `test/us_extract/client_test.py::TestClient::test_result_correctly_assigned_to_corresponding_lookup: passed != not found`
- `test/us_extract/client_test.py::TestClient::test_sending_body_only_lookup: passed != not found`
- `test/us_extract/client_test.py::TestClient::test_sending_fully_populated_lookup: passed != not found`
- `test/us_extract/result_test.py::TestResult::test_all_fields_filled_correctly: passed != not found`
- `test/us_reverse_geo/client_test.py::TestClient::test_sending_freeform_lookup: passed != not found`
- `test/us_street/batch_test.py::TestBatch::test_adding_a_lookup_when_batch_is_full_raises_exception: passed != not found`
- `test/us_street/batch_test.py::TestBatch::test_clear_method_clears_both_lookup_collections: passed != not found`
- `test/us_street/batch_test.py::TestBatch::test_gets_lookup_by_index: passed != not found`
- `test/us_street/batch_test.py::TestBatch::test_gets_lookup_by_input_id: passed != not found`
- `test/us_street/batch_test.py::TestBatch::test_returns_correct_size: passed != not found`
- `test/us_street/client_test.py::TestClient::test_candidates_correctly_assigned_to_corresponding_lookup: passed != not found`
- `test/us_street/client_test.py::TestClient::test_deserialize_called_with_response_body: passed != not found`
- `test/us_street/client_test.py::TestClient::test_empty_batch_not_sent: passed != not found`
- `test/us_street/client_test.py::TestClient::test_freeform_assigned_to_street_field: passed != not found`
- `test/us_street/client_test.py::TestClient::test_full_json_response_deserialization: passed != not found`
- `test/us_street/client_test.py::TestClient::test_raises_exception_when_response_has_error: passed != not found`
- `test/us_street/client_test.py::TestClient::test_single_lookup_values_correctly_assigned_to_parameters: passed != not found`
- `test/us_street/client_test.py::TestClient::test_successfully_sends_batch: passed != not found`
- `test/us_zipcode/client_test.py::TestClient::test_Successfully_Sends_Batch: passed != not found`
- `test/us_zipcode/client_test.py::TestClient::test_deserialize_called_with_response_body: passed != not found`
- `test/us_zipcode/client_test.py::TestClient::test_empty_batch_not_sent: passed != not found`
- `test/us_zipcode/client_test.py::TestClient::test_raises_exception_when_response_has_error: passed != not found`
- `test/us_zipcode/client_test.py::TestClient::test_results_correctly_assigned_to_corresponding_lookup: passed != not found`
- `test/us_zipcode/client_test.py::TestClient::test_single_lookup_values_correctly_assigned_to_parameters: passed != not found`
- `test/x_forwarded_for_test.py::TestCustomHeaderSender::test_custom_headers_used: passed != not found`
- `test/x_forwarded_for_test.py::TestCustomHeaderSender::test_populates_header: passed != not found`
- `test/x_forwarded_for_test.py::TestCustomHeaderSender::test_x_forwarded_for_header_set: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
