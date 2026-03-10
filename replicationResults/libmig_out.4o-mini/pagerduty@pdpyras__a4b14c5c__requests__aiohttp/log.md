## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/pagerduty@pdpyras__a4b14c5c__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating pdpyras.py
### migrating test_pdpyras.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test_pdpyras.py::APISessionTest::test_find: passed != not found`
- `test_pdpyras.py::APISessionTest::test_iter_all: passed != not found`
- `test_pdpyras.py::APISessionTest::test_iter_cursor: passed != not found`
- `test_pdpyras.py::APISessionTest::test_oauth_headers: passed != not found`
- `test_pdpyras.py::APISessionTest::test_persist: passed != not found`
- `test_pdpyras.py::APISessionTest::test_postprocess: passed != not found`
- `test_pdpyras.py::APISessionTest::test_print_debug: passed != not found`
- `test_pdpyras.py::APISessionTest::test_request: passed != not found`
- `test_pdpyras.py::APISessionTest::test_rget: passed != not found`
- `test_pdpyras.py::APISessionTest::test_subdomain: passed != not found`
- `test_pdpyras.py::APISessionTest::test_truncated_token: passed != not found`
- `test_pdpyras.py::ChangeEventsSessionTest::test_submit_change_event: passed != not found`
- `test_pdpyras.py::ChangeEventsSessionTest::test_submit_lite_change_event: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_entity_wrappers: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_infer_entity_wrapper: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_unwrap: passed != not found`
- `test_pdpyras.py::EventsSessionTest::test_send_event: passed != not found`
- `test_pdpyras.py::EventsSessionTest::test_send_explicit_event: passed != not found`
- `test_pdpyras.py::FunctionDecoratorsTest::test_resource_path: passed != not found`
- `test_pdpyras.py::FunctionDecoratorsTest::test_wrapped_entities: passed != not found`
- `test_pdpyras.py::HelperFunctionsTest::test_plural_deplural: passed != not found`
- `test_pdpyras.py::HelperFunctionsTest::test_successful_response: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_canonical_path: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_is_path_param: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_normalize_url: passed != not found`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test_pdpyras.py::APISessionTest::test_find: passed != not found`
- `test_pdpyras.py::APISessionTest::test_iter_all: passed != not found`
- `test_pdpyras.py::APISessionTest::test_iter_cursor: passed != not found`
- `test_pdpyras.py::APISessionTest::test_oauth_headers: passed != not found`
- `test_pdpyras.py::APISessionTest::test_persist: passed != not found`
- `test_pdpyras.py::APISessionTest::test_postprocess: passed != not found`
- `test_pdpyras.py::APISessionTest::test_print_debug: passed != not found`
- `test_pdpyras.py::APISessionTest::test_request: passed != not found`
- `test_pdpyras.py::APISessionTest::test_rget: passed != not found`
- `test_pdpyras.py::APISessionTest::test_subdomain: passed != not found`
- `test_pdpyras.py::APISessionTest::test_truncated_token: passed != not found`
- `test_pdpyras.py::ChangeEventsSessionTest::test_submit_change_event: passed != not found`
- `test_pdpyras.py::ChangeEventsSessionTest::test_submit_lite_change_event: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_entity_wrappers: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_infer_entity_wrapper: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_unwrap: passed != not found`
- `test_pdpyras.py::EventsSessionTest::test_send_event: passed != not found`
- `test_pdpyras.py::EventsSessionTest::test_send_explicit_event: passed != not found`
- `test_pdpyras.py::FunctionDecoratorsTest::test_resource_path: passed != not found`
- `test_pdpyras.py::FunctionDecoratorsTest::test_wrapped_entities: passed != not found`
- `test_pdpyras.py::HelperFunctionsTest::test_plural_deplural: passed != not found`
- `test_pdpyras.py::HelperFunctionsTest::test_successful_response: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_canonical_path: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_is_path_param: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_normalize_url: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 17 functions to mark async including 16 tests
- Found 2 calls to await
- 2 files requires transformation
- transforming test_pdpyras.py
- transforming pdpyras.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test_pdpyras.py::APISessionTest::test_find: passed != not found`
- `test_pdpyras.py::APISessionTest::test_iter_all: passed != not found`
- `test_pdpyras.py::APISessionTest::test_iter_cursor: passed != not found`
- `test_pdpyras.py::APISessionTest::test_oauth_headers: passed != not found`
- `test_pdpyras.py::APISessionTest::test_persist: passed != not found`
- `test_pdpyras.py::APISessionTest::test_postprocess: passed != not found`
- `test_pdpyras.py::APISessionTest::test_print_debug: passed != not found`
- `test_pdpyras.py::APISessionTest::test_request: passed != not found`
- `test_pdpyras.py::APISessionTest::test_rget: passed != not found`
- `test_pdpyras.py::APISessionTest::test_subdomain: passed != not found`
- `test_pdpyras.py::APISessionTest::test_truncated_token: passed != not found`
- `test_pdpyras.py::ChangeEventsSessionTest::test_submit_change_event: passed != not found`
- `test_pdpyras.py::ChangeEventsSessionTest::test_submit_lite_change_event: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_entity_wrappers: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_infer_entity_wrapper: passed != not found`
- `test_pdpyras.py::EntityWrappingTest::test_unwrap: passed != not found`
- `test_pdpyras.py::EventsSessionTest::test_send_event: passed != not found`
- `test_pdpyras.py::EventsSessionTest::test_send_explicit_event: passed != not found`
- `test_pdpyras.py::FunctionDecoratorsTest::test_resource_path: passed != not found`
- `test_pdpyras.py::FunctionDecoratorsTest::test_wrapped_entities: passed != not found`
- `test_pdpyras.py::HelperFunctionsTest::test_plural_deplural: passed != not found`
- `test_pdpyras.py::HelperFunctionsTest::test_successful_response: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_canonical_path: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_is_path_param: passed != not found`
- `test_pdpyras.py::URLHandlingTest::test_normalize_url: passed != not found`
- async_transform finished
