## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/jacob-y@django-clean-architecture__103d89e4__requests__pycurl/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating modules/Application/PluginAdaptors/HTTPMixin.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/Unit/Application/test_paypal_adaptor.py::PayPalAdaptorTest::test_capture: passed != failed`
- `tests/Unit/Application/test_paypal_adaptor.py::PayPalAdaptorTest::test_create: passed != failed`
- `tests/Unit/Application/test_paypal_adaptor.py::PayPalAdaptorTest::test_status: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
