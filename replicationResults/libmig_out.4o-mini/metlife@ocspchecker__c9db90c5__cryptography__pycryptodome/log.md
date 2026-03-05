## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/metlife@ocspchecker__c9db90c5__cryptography__pycryptodome/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating ocspchecker/ocspchecker.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_ocspchecker.py::test_end_to_end_success_test: passed != failed`
- `tests/test_ocspchecker.py::test_extract_ocsp_result_success: passed != failed`
- `tests/test_ocspchecker.py::test_extract_ocsp_result_unauthorized: passed != failed`
- `tests/test_ocspchecker.py::test_extract_ocsp_url_success: passed != failed`
- `tests/test_ocspchecker.py::test_no_port_supplied: passed != failed`
- `tests/test_ocspchecker.py::test_strip_http_from_host: passed != failed`
- `tests/test_ocspchecker.py::test_strip_https_from_host: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[amazontrust.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[certum.pl]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[comodoca.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[digicert.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[entrustdatacard.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[globalsign.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[identrust.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[microsoft.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[networksolutions.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[secom.co.jp]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[sectigo.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[trustwave.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[wisekey.com]: passed != failed`
- `tests/test_responders.py::test_a_cert_from_each_root_ca[www.godaddy.com]: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
