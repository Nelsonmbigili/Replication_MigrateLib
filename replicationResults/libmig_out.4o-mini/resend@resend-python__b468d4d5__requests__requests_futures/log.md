## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/resend@resend-python__b468d4d5__requests__requests_futures/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating resend/request.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/api_keys_test.py::TestResendApiKeys::test_api_keys_create: passed != failed`
- `tests/api_keys_test.py::TestResendApiKeys::test_api_keys_list: passed != failed`
- `tests/api_keys_test.py::TestResendApiKeys::test_api_keys_remove: passed != failed`
- `tests/api_keys_test.py::TestResendApiKeys::test_should_create_api_key_raise_exception_when_no_content: passed != failed`
- `tests/api_keys_test.py::TestResendApiKeys::test_should_list_api_key_raise_exception_when_no_content: passed != failed`
- `tests/audiences_test.py::TestResendAudiences::test_audiences_create: passed != failed`
- `tests/audiences_test.py::TestResendAudiences::test_audiences_get: passed != failed`
- `tests/audiences_test.py::TestResendAudiences::test_audiences_list: passed != failed`
- `tests/audiences_test.py::TestResendAudiences::test_audiences_remove: passed != failed`
- `tests/audiences_test.py::TestResendAudiences::test_should_create_audiences_raise_exception_when_no_content: passed != failed`
- `tests/audiences_test.py::TestResendAudiences::test_should_get_audiences_raise_exception_when_no_content: passed != failed`
- `tests/audiences_test.py::TestResendAudiences::test_should_list_audiences_raise_exception_when_no_content: passed != failed`
- `tests/audiences_test.py::TestResendAudiences::test_should_remove_audiences_raise_exception_when_no_content: passed != failed`
- `tests/batch_emails_test.py::TestResendBatchSend::test_batch_email_send: passed != failed`
- `tests/batch_emails_test.py::TestResendBatchSend::test_should_send_batch_email_raise_exception_when_no_content: passed != failed`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_create: passed != failed`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_get: passed != failed`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_list: passed != failed`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_remove: passed != failed`
- `tests/broadcasts_test.py::TestResendBroadcasts::test_broadcasts_send: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_contacts_create: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_contacts_get: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_contacts_list: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_contacts_remove_by_email: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_contacts_remove_by_id: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_contacts_update: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_should_create_contacts_raise_exception_when_no_content: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_should_get_contacts_raise_exception_when_no_content: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_should_list_contacts_raise_exception_when_no_content: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_should_remove_contacts_by_email_raise_exception_when_no_content: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_should_remove_contacts_by_id_raise_exception_when_no_content: passed != failed`
- `tests/contacts_test.py::TestResendContacts::test_should_update_contacts_raise_exception_when_no_content: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_domains_create: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_domains_get: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_domains_list: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_domains_remove: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_domains_update: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_domains_verify: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_should_create_domains_raise_exception_when_no_content: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_should_get_domains_raise_exception_when_no_content: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_should_list_domains_raise_exception_when_no_content: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_should_remove_domains_raise_exception_when_no_content: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_should_update_domains_raise_exception_when_no_content: passed != failed`
- `tests/domains_test.py::TestResendDomains::test_should_verify_domains_raise_exception_when_no_content: passed != failed`
- `tests/emails_test.py::TestResendEmail::test_cancel_scheduled_email: passed != failed`
- `tests/emails_test.py::TestResendEmail::test_email_get: passed != failed`
- `tests/emails_test.py::TestResendEmail::test_email_send_with_from: passed != failed`
- `tests/emails_test.py::TestResendEmail::test_should_get_email_raise_exception_when_no_content: passed != failed`
- `tests/emails_test.py::TestResendEmail::test_should_send_email_raise_exception_when_no_content: passed != failed`
- `tests/emails_test.py::TestResendEmail::test_update_email: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
