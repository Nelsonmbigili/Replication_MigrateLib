## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/filestack@filestack-python__0e44e337__requests__urllib3/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 11 files
### migrating filestack/mixins/common.py
### migrating filestack/mixins/imagetransformation.py
### migrating filestack/models/audiovisual.py
### migrating filestack/models/client.py
### migrating filestack/models/filelink.py
### migrating filestack/uploads/external_url.py
### migrating filestack/uploads/intelligent_ingestion.py
### migrating filestack/uploads/multipart.py
### migrating filestack/utils.py
### migrating tests/multipart_test.py
### migrating tests/utils_test.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/audiovisual_test.py::test_convert: passed != failed`
- `tests/audiovisual_test.py::test_status: passed != failed`
- `tests/client_test.py::test_store_external_url: passed != failed`
- `tests/client_test.py::test_zip: passed != failed`
- `tests/filelink_test.py::test_bad_call: passed != failed`
- `tests/filelink_test.py::test_download: passed != failed`
- `tests/filelink_test.py::test_get_content: passed != failed`
- `tests/filelink_test.py::test_metadata[None-None-expected_params0]: passed != failed`
- `tests/filelink_test.py::test_metadata[None-security1-expected_params1]: passed != failed`
- `tests/filelink_test.py::test_metadata[attributes2-security2-expected_params2]: passed != failed`
- `tests/filelink_test.py::test_overwrite_with_file_obj: passed != failed`
- `tests/filelink_test.py::test_overwrite_with_filepath: passed != failed`
- `tests/filelink_test.py::test_overwrite_with_url[False]: passed != failed`
- `tests/filelink_test.py::test_overwrite_with_url[True]: passed != failed`
- `tests/filelink_test.py::test_sfw: passed != failed`
- `tests/filelink_test.py::test_sfw_on_transformation: passed != failed`
- `tests/filelink_test.py::test_successful_delete[flink0-security_arg0]: passed != failed`
- `tests/filelink_test.py::test_successful_delete[flink1-None]: passed != failed`
- `tests/filelink_test.py::test_tags: passed != failed`
- `tests/filelink_test.py::test_tags_on_transformation: passed != failed`
- `tests/intelligent_ingestion_test.py::test_min_chunk_size_exception: passed != failed`
- `tests/intelligent_ingestion_test.py::test_upload_part_success: passed != failed`
- `tests/intelligent_ingestion_test.py::test_upload_part_with_resize: passed != failed`
- `tests/multipart_test.py::test_upload_chunk: passed != failed`
- `tests/multipart_test.py::test_upload_file_obj: passed != failed`
- `tests/multipart_test.py::test_upload_filepath: passed != failed`
- `tests/multipart_test.py::test_upload_with_workflows: passed != failed`
- `tests/transformation_test.py::test_av_convert: passed != failed`
- `tests/transformation_test.py::test_chain_tasks_and_store: passed != failed`
- `tests/uploads/test_upload_external_url.py::test_upload_with_store_params[S3,-store_params0-None-expected_store_tasks0]: passed != failed`
- `tests/uploads/test_upload_external_url.py::test_upload_with_store_params[gcs-store_params1-SecurityMock-expected_store_tasks1]: passed != failed`
- `tests/utils_test.py::test_req_wrapper_overwrite_headers: passed != failed`
- `tests/utils_test.py::test_req_wrapper_raise_exception: passed != failed`
- `tests/utils_test.py::test_req_wrapper_use_provided_headers: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
