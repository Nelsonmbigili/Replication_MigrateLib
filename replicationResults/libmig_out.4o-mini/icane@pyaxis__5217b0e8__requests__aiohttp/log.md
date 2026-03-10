## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/icane@pyaxis__5217b0e8__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating pyaxis/pyaxis.py
### migrating pyaxis/test/integration/test_pyaxis.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `pyaxis/test/integration/test_pyaxis.py::test_build_dataframe: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_connection_error: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_get_dimensions: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_http_error: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_metadata_extract: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_metadata_split_to_dict: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_read: passed != failed`
- `pyaxis/test/unit/test_json_stat.py::test_to_json_stat: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_build_dataframe: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_get_codes: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_get_default_lang: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_get_dimensions: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_metadata_dict_maker: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_metadata_extract: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_metadata_split_to_dict: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_multilingual_checker: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_multilingual_parse: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_read: passed != failed`
- `pyaxis/test/unit/test_pyaxis.py::test_translation_dict_maker: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 24 functions to mark async including 22 tests
- Found 23 calls to await
- 4 files requires transformation
- transforming pyaxis/test/unit/test_json_stat.py
- transforming pyaxis/pyaxis.py
- transforming pyaxis/test/unit/test_pyaxis.py
- transforming pyaxis/test/integration/test_pyaxis.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `pyaxis/test/integration/test_pyaxis.py::test_build_dataframe: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_connection_error: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_get_dimensions: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_http_error: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_metadata_extract: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_metadata_split_to_dict: passed != failed`
- `pyaxis/test/integration/test_pyaxis.py::test_read: passed != failed`
- async_transform finished
