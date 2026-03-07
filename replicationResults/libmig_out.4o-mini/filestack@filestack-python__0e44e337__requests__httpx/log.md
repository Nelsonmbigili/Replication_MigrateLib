## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/filestack@filestack-python__0e44e337__requests__httpx/.venv
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
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/audiovisual_test.py::test_convert: passed != not found`
- `tests/audiovisual_test.py::test_status: passed != not found`
- `tests/client_test.py::test_api_set: passed != not found`
- `tests/client_test.py::test_security_inheritance: passed != not found`
- `tests/client_test.py::test_store_external_url: passed != not found`
- `tests/client_test.py::test_store_filepath: passed != not found`
- `tests/client_test.py::test_transform_external: passed != not found`
- `tests/client_test.py::test_url_screenshot: passed != not found`
- `tests/client_test.py::test_wrong_storage: passed != not found`
- `tests/client_test.py::test_zip: passed != not found`
- `tests/filelink_test.py::test_bad_call: passed != not found`
- `tests/filelink_test.py::test_delete_without_apikey_or_security[flink0-Security is required]: passed != not found`
- `tests/filelink_test.py::test_delete_without_apikey_or_security[flink1-Apikey is required]: passed != not found`
- `tests/filelink_test.py::test_download: passed != not found`
- `tests/filelink_test.py::test_get_content: passed != not found`
- `tests/filelink_test.py::test_handle: passed != not found`
- `tests/filelink_test.py::test_invalid_overwrite_call: passed != not found`
- `tests/filelink_test.py::test_metadata[None-None-expected_params0]: passed != not found`
- `tests/filelink_test.py::test_metadata[None-security1-expected_params1]: passed != not found`
- `tests/filelink_test.py::test_metadata[attributes2-security2-expected_params2]: passed != not found`
- `tests/filelink_test.py::test_overwrite_with_file_obj: passed != not found`
- `tests/filelink_test.py::test_overwrite_with_filepath: passed != not found`
- `tests/filelink_test.py::test_overwrite_with_url[False]: passed != not found`
- `tests/filelink_test.py::test_overwrite_with_url[True]: passed != not found`
- `tests/filelink_test.py::test_overwrite_without_security: passed != not found`
- `tests/filelink_test.py::test_sfw: passed != not found`
- `tests/filelink_test.py::test_sfw_on_transformation: passed != not found`
- `tests/filelink_test.py::test_sfw_without_security: passed != not found`
- `tests/filelink_test.py::test_signed_url[None-security=p:eyJjYWxsIjogWyJyZWFkIl0sICJleHBpcnkiOiAxMDIzODIzOX0=,s:858d1ee9c0a1f06283e495f78dc7950ff6e64136ce960465f35539791fcd486b]: passed != not found`
- `tests/filelink_test.py::test_signed_url[security_obj1-security=p:eyJjYWxsIjogWyJ3cml0ZSJdLCAiZXhwaXJ5IjogMTY1NTk5MjQzMn0=,s:625cc5b9beab3e939fb53935f7795919c9f57f628d43adfc14566d2ad9a4ad47]: passed != not found`
- `tests/filelink_test.py::test_successful_delete[flink0-security_arg0]: passed != not found`
- `tests/filelink_test.py::test_successful_delete[flink1-None]: passed != not found`
- `tests/filelink_test.py::test_tags: passed != not found`
- `tests/filelink_test.py::test_tags_on_transformation: passed != not found`
- `tests/filelink_test.py::test_tags_without_security: passed != not found`
- `tests/filelink_test.py::test_url: passed != not found`
- `tests/filestack_helpers_test.py::test_agrument_validation[1-body-headers1-value is not a string]: passed != not found`
- `tests/filestack_helpers_test.py::test_agrument_validation[hook-secret--headers2-fs-signature header is missing]: passed != not found`
- `tests/filestack_helpers_test.py::test_agrument_validation[hook-secret-body-should be a dict-value is not a dict]: passed != not found`
- `tests/filestack_helpers_test.py::test_agrument_validation[hook-secret-body3-headers3-Invalid webhook body]: passed != not found`
- `tests/filestack_helpers_test.py::test_webhook_verification[57cbb25386c3d6ff758a7a75cf52ba02cf2b0a1a2d6d5dfb9c886553ca6011cb-True]: passed != not found`
- `tests/filestack_helpers_test.py::test_webhook_verification[incorrect-signature-False]: passed != not found`
- `tests/intelligent_ingestion_test.py::test_min_chunk_size_exception: passed != not found`
- `tests/intelligent_ingestion_test.py::test_upload_part_success: passed != not found`
- `tests/intelligent_ingestion_test.py::test_upload_part_with_resize: passed != not found`
- `tests/multipart_test.py::test_upload_chunk: passed != not found`
- `tests/multipart_test.py::test_upload_file_obj: passed != not found`
- `tests/multipart_test.py::test_upload_filepath: passed != not found`
- `tests/multipart_test.py::test_upload_with_workflows: passed != not found`
- `tests/security_test.py::test_security: passed != not found`
- `tests/security_test.py::test_security_as_url_string: passed != not found`
- `tests/tasks_test.py::test_animate: passed != not found`
- `tests/tasks_test.py::test_createpdf: passed != not found`
- `tests/tasks_test.py::test_doc_to_images: passed != not found`
- `tests/tasks_test.py::test_fallback: passed != not found`
- `tests/tasks_test.py::test_pdf_convert: passed != not found`
- `tests/tasks_test.py::test_smart_crop: passed != not found`
- `tests/transformation_test.py::test_ascii: passed != not found`
- `tests/transformation_test.py::test_auto_image: passed != not found`
- `tests/transformation_test.py::test_av_convert: passed != not found`
- `tests/transformation_test.py::test_blackwhite: passed != not found`
- `tests/transformation_test.py::test_blur: passed != not found`
- `tests/transformation_test.py::test_border: passed != not found`
- `tests/transformation_test.py::test_chain_tasks_and_store: passed != not found`
- `tests/transformation_test.py::test_circle: passed != not found`
- `tests/transformation_test.py::test_collage: passed != not found`
- `tests/transformation_test.py::test_crop: passed != not found`
- `tests/transformation_test.py::test_crop_faces: passed != not found`
- `tests/transformation_test.py::test_detect_faces: passed != not found`
- `tests/transformation_test.py::test_enhance: passed != not found`
- `tests/transformation_test.py::test_fallback: passed != not found`
- `tests/transformation_test.py::test_filetype_conversion: passed != not found`
- `tests/transformation_test.py::test_flip: passed != not found`
- `tests/transformation_test.py::test_flop: passed != not found`
- `tests/transformation_test.py::test_minify_css: passed != not found`
- `tests/transformation_test.py::test_minify_css_with_params: passed != not found`
- `tests/transformation_test.py::test_minify_js: passed != not found`
- `tests/transformation_test.py::test_modulate: passed != not found`
- `tests/transformation_test.py::test_monochrome: passed != not found`
- `tests/transformation_test.py::test_negative: passed != not found`
- `tests/transformation_test.py::test_no_metadata: passed != not found`
- `tests/transformation_test.py::test_oil_paint: passed != not found`
- `tests/transformation_test.py::test_partial_blur: passed != not found`
- `tests/transformation_test.py::test_partial_pixelate: passed != not found`
- `tests/transformation_test.py::test_pdf_convert: passed != not found`
- `tests/transformation_test.py::test_pdf_info: passed != not found`
- `tests/transformation_test.py::test_pixelate: passed != not found`
- `tests/transformation_test.py::test_pixelate_faces: passed != not found`
- `tests/transformation_test.py::test_polaroid: passed != not found`
- `tests/transformation_test.py::test_redeye: passed != not found`
- `tests/transformation_test.py::test_resize: passed != not found`
- `tests/transformation_test.py::test_rotate: passed != not found`
- `tests/transformation_test.py::test_round_corners: passed != not found`
- `tests/transformation_test.py::test_sanity: passed != not found`
- `tests/transformation_test.py::test_sepia: passed != not found`
- `tests/transformation_test.py::test_shadow: passed != not found`
- `tests/transformation_test.py::test_sharpen: passed != not found`
- `tests/transformation_test.py::test_torn_edges: passed != not found`
- `tests/transformation_test.py::test_upscale: passed != not found`
- `tests/transformation_test.py::test_vignette: passed != not found`
- `tests/transformation_test.py::test_watermark: passed != not found`
- `tests/transformation_test.py::test_zip: passed != not found`
- `tests/uploads/test_upload_external_url.py::test_upload_with_store_params[S3,-store_params0-None-expected_store_tasks0]: passed != not found`
- `tests/uploads/test_upload_external_url.py::test_upload_with_store_params[gcs-store_params1-SecurityMock-expected_store_tasks1]: passed != not found`
- `tests/utils_test.py::test_req_wrapper_overwrite_headers: passed != not found`
- `tests/utils_test.py::test_req_wrapper_raise_exception: passed != not found`
- `tests/utils_test.py::test_req_wrapper_use_provided_headers: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
