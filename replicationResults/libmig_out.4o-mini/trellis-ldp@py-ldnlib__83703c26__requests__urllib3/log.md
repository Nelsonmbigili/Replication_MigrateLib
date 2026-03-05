## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/trellis-ldp@py-ldnlib__83703c26__requests__urllib3/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 3 files
### migrating ldnlib/base.py
### migrating ldnlib/consumer.py
### migrating ldnlib/sender.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_base.py::TestBase::test_discover_get: passed != failed`
- `tests/test_base.py::TestBase::test_discover_head: passed != failed`
- `tests/test_consumer.py::TestConsumer::test_notification_jsonld: passed != failed`
- `tests/test_consumer.py::TestConsumer::test_notification_turtle: passed != failed`
- `tests/test_consumer.py::TestConsumer::test_notifications_jsonld_compacted: passed != failed`
- `tests/test_consumer.py::TestConsumer::test_notifications_jsonld_expanded: passed != failed`
- `tests/test_consumer.py::TestConsumer::test_notifications_ntriples: passed != failed`
- `tests/test_consumer.py::TestConsumer::test_notifications_turtle: passed != failed`
- `tests/test_sender.py::TestSender::test_send_dict: passed != failed`
- `tests/test_sender.py::TestSender::test_send_graph: passed != failed`
- `tests/test_sender.py::TestSender::test_send_list: passed != failed`
- `tests/test_sender.py::TestSender::test_send_string: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
