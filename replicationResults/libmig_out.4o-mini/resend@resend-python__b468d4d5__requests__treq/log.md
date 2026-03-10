## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/resend@resend-python__b468d4d5__requests__treq/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating resend/request.py
### running tests
- test finished with status 4, cov finished with status 1
### test diff with round premig
- `tests/api_keys_test.py::TestResendApiKeys::test_api_keys_create: passed != not found`
- `tests/api_keys_test.py::TestResendApiKeys::test_api_keys_list: passed != not found`
- `tests/api_keys_test.py::TestResendApiKeys::test_api_keys_remove: passed != not found`
- `tests/api_keys_test.py::TestResendApiKeys::test_should_create_api_key_raise_exception_when_no_content: passed != not found`
- `tests/api_keys_test.py::TestResendApiKeys::test_should_list_api_key_raise_exception_when_no_content: passed != not found`
- `tests/audiences_test.py::TestResendAudiences::test_audiences_create: passed != not found`
- `tests/audiences_test.py::TestResendAudiences::test_audiences_get: passed != not found`
- `tests/audiences_test.py::TestResendAudiences::test_audiences_list: passed != not found`
- `tests/audiences_test.py::TestResendAudiences::test_audiences_remove: passed != not found`
- `tests/audiences_test.py::TestResendAudiences::test_should_create_audiences_raise_exception_when_no_content: passed != not found`
- `tests/audiences_test.py::TestResendAudiences::test_should_get_audiences_raise_exception_when_no_content: passed != not found`
- `tests/audiences_test.py::TestResendAudiences::test_should_list_audiences_raise_exception_when_no_content: passed != not found`
- `tests/audiences_test.py::TestResendAudiences::test_should_remove_audiences_raise_exception_when_no_content: passed != not found`
- `tests/batch_emails_test.py::TestResendBatchSend::test_batch_email_send: passed != not found`
- `tests/batch_emails_test.py::TestResendBatchSend::test_should_send_batch_email_raise_exception_when_no_content: passed != not found`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_create: passed != not found`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_get: passed != not found`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_list: passed != not found`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_remove: passed != not found`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_send: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_contacts_create: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_contacts_get: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_contacts_list: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_contacts_remove_by_email: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_contacts_remove_by_id: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_contacts_remove_raises: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_contacts_update: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_should_create_contacts_raise_exception_when_no_content: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_should_get_contacts_raise_exception_when_no_content: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_should_list_contacts_raise_exception_when_no_content: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_should_remove_contacts_by_email_raise_exception_when_no_content: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_should_remove_contacts_by_id_raise_exception_when_no_content: passed != not found`
- `tests/contacts_test.py::TestResendContacts::test_should_update_contacts_raise_exception_when_no_content: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_domains_create: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_domains_get: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_domains_list: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_domains_remove: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_domains_update: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_domains_verify: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_should_create_domains_raise_exception_when_no_content: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_should_get_domains_raise_exception_when_no_content: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_should_list_domains_raise_exception_when_no_content: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_should_remove_domains_raise_exception_when_no_content: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_should_update_domains_raise_exception_when_no_content: passed != not found`
- `tests/domains_test.py::TestResendDomains::test_should_verify_domains_raise_exception_when_no_content: passed != not found`
- `tests/emails_test.py::TestResendEmail::test_cancel_scheduled_email: passed != not found`
- `tests/emails_test.py::TestResendEmail::test_email_get: passed != not found`
- `tests/emails_test.py::TestResendEmail::test_email_response_html: passed != not found`
- `tests/emails_test.py::TestResendEmail::test_email_send_with_from: passed != not found`
- `tests/emails_test.py::TestResendEmail::test_should_get_email_raise_exception_when_no_content: passed != not found`
- `tests/emails_test.py::TestResendEmail::test_should_send_email_raise_exception_when_no_content: passed != not found`
- `tests/emails_test.py::TestResendEmail::test_update_email: passed != not found`
- `tests/exceptions_test.py::TestResendError::test_error_500: passed != not found`
- `tests/exceptions_test.py::TestResendError::test_raise_known_error: passed != not found`
- `tests/exceptions_test.py::TestResendError::test_raise_when_unknown_error: passed != not found`
- `tests/exceptions_test.py::TestResendError::test_validation_error_from_400: passed != not found`
- `tests/exceptions_test.py::TestResendError::test_validation_error_from_422: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
