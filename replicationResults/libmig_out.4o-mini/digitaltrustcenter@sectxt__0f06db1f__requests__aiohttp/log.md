## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/digitaltrustcenter@sectxt__0f06db1f__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating sectxt/__init__.py
### migrating test/test_sectxt.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test/test_sectxt.py::SecTxtTestCase::test_byte_order_mark: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_byte_order_mark_parser: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_contact_field_properties: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_csaf_https_uri: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_csaf_provider_file: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_empty_key: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_empty_key2: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_expired: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_future_expires: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_invalid_expires: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_invalid_uri_scheme: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_local_file: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_long_expiry: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_missing_space: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_missing_value: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_multiple_csaf_notification: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_https: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_line_separators: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_uri: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_not_correct_path: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_pgp_signed_formatting: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_prec_ws: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_preferred_languages: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_dash_escaped: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_invalid_pgp: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_no_canonical: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_too_many_final_newlines_signed: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_unknown_fields: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_valid_security_txt: passed != not found`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test/test_sectxt.py::SecTxtTestCase::test_byte_order_mark: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_byte_order_mark_parser: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_contact_field_properties: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_csaf_https_uri: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_csaf_provider_file: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_empty_key: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_empty_key2: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_expired: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_future_expires: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_invalid_expires: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_invalid_uri_scheme: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_local_file: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_long_expiry: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_missing_space: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_missing_value: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_multiple_csaf_notification: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_https: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_line_separators: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_uri: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_not_correct_path: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_pgp_signed_formatting: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_prec_ws: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_preferred_languages: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_dash_escaped: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_invalid_pgp: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_no_canonical: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_too_many_final_newlines_signed: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_unknown_fields: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_valid_security_txt: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 34 functions to mark async including 31 tests
- Found 40 calls to await
- 2 files requires transformation
- transforming sectxt/__init__.py
- transforming test/test_sectxt.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test/test_sectxt.py::SecTxtTestCase::test_byte_order_mark: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_byte_order_mark_parser: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_contact_field_properties: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_csaf_https_uri: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_csaf_provider_file: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_empty_key: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_empty_key2: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_expired: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_future_expires: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_invalid_expires: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_invalid_uri_scheme: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_local_file: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_long_expiry: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_missing_space: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_missing_value: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_multiple_csaf_notification: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_https: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_line_separators: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_no_uri: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_not_correct_path: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_pgp_signed_formatting: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_prec_ws: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_preferred_languages: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_dash_escaped: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_invalid_pgp: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_signed_no_canonical: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_too_many_final_newlines_signed: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_unknown_fields: passed != not found`
- `test/test_sectxt.py::SecTxtTestCase::test_valid_security_txt: passed != not found`
- async_transform finished
