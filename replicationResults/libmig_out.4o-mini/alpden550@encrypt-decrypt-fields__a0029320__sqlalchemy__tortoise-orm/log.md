## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/alpden550@encrypt-decrypt-fields__a0029320__sqlalchemy__tortoise-orm/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating encrypt_decrypt_fields/orm/alchemy_fields.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_decrypt_empty_value: passed != not found`
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_decrypt_successfully: passed != not found`
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_encrypt_not_successfully[dict]: passed != not found`
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_encrypt_not_successfully[int]: passed != not found`
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_encrypt_not_successfully[list]: passed != not found`
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_encrypt_not_successfully[tuple]: passed != not found`
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_encrypt_successfully: passed != not found`
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_key_is_str: passed != not found`
- `encrypt_decrypt_fields/tests/test_crypto.py::TestCrypt::test_key_not_str: passed != not found`
- `encrypt_decrypt_fields/tests/test_django_field.py::TestDjangoEncryptField::test_passed_any_value[1-int]: passed != not found`
- `encrypt_decrypt_fields/tests/test_django_field.py::TestDjangoEncryptField::test_passed_any_value[passed1-dict]: passed != not found`
- `encrypt_decrypt_fields/tests/test_django_field.py::TestDjangoEncryptField::test_passed_any_value[passed2-list]: passed != not found`
- `encrypt_decrypt_fields/tests/test_django_field.py::TestDjangoEncryptField::test_passed_byte_value: passed != not found`
- `encrypt_decrypt_fields/tests/test_django_field.py::TestDjangoEncryptField::test_passed_empty_value: passed != not found`
- `encrypt_decrypt_fields/tests/test_django_field.py::TestDjangoEncryptField::test_passed_memoryview_value: passed != not found`
- `encrypt_decrypt_fields/tests/test_django_field.py::TestDjangoEncryptField::test_passed_string_value: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
