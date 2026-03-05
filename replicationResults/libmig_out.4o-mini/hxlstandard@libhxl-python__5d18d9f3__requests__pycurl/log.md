## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/hxlstandard@libhxl-python__5d18d9f3__requests__pycurl/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating hxl/input.py
### migrating hxl/scripts.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_input.py::TestBadInput::test_bad_url: passed != failed`
- `tests/test_input.py::TestInput::test_ckan_dataset: passed != failed`
- `tests/test_input.py::TestInput::test_ckan_resource: passed != failed`
- `tests/test_input.py::TestInput::test_optional_params: passed != failed`
- `tests/test_input.py::TestParser::test_remote_csv: passed != failed`
- `tests/test_input.py::TestParser::test_remote_csv_hxl_ext: passed != failed`
- `tests/test_input.py::TestParser::test_remote_xls: passed != failed`
- `tests/test_input.py::TestParser::test_remote_xlsx: passed != failed`
- `tests/test_input.py::TestUntaggedInput::test_html: passed != failed`
- `tests/test_scripts.py::TestAdd::test_before: passed != failed`
- `tests/test_scripts.py::TestAdd::test_default: passed != failed`
- `tests/test_scripts.py::TestAdd::test_headers: passed != failed`
- `tests/test_scripts.py::TestAppend::test_append: passed != failed`
- `tests/test_scripts.py::TestClean::test_case: passed != failed`
- `tests/test_scripts.py::TestClean::test_headers: passed != failed`
- `tests/test_scripts.py::TestClean::test_noheaders: passed != failed`
- `tests/test_scripts.py::TestClean::test_whitespace: passed != failed`
- `tests/test_scripts.py::TestCount::test_aggregated: passed != failed`
- `tests/test_scripts.py::TestCount::test_count_colspec: passed != failed`
- `tests/test_scripts.py::TestCount::test_simple: passed != failed`
- `tests/test_scripts.py::TestCut::test_excludes: passed != failed`
- `tests/test_scripts.py::TestCut::test_includes: passed != failed`
- `tests/test_scripts.py::TestMerge::test_merge: passed != failed`
- `tests/test_scripts.py::TestMerge::test_overwrite: passed != failed`
- `tests/test_scripts.py::TestMerge::test_replace: passed != failed`
- `tests/test_scripts.py::TestRename::test_header: passed != failed`
- `tests/test_scripts.py::TestRename::test_multiple: passed != failed`
- `tests/test_scripts.py::TestRename::test_single: passed != failed`
- `tests/test_scripts.py::TestSelect::test_eq: passed != failed`
- `tests/test_scripts.py::TestSelect::test_ge: passed != failed`
- `tests/test_scripts.py::TestSelect::test_gt: passed != failed`
- `tests/test_scripts.py::TestSelect::test_le: passed != failed`
- `tests/test_scripts.py::TestSelect::test_lt: passed != failed`
- `tests/test_scripts.py::TestSelect::test_multiple: passed != failed`
- `tests/test_scripts.py::TestSelect::test_ne: passed != failed`
- `tests/test_scripts.py::TestSelect::test_nre: passed != failed`
- `tests/test_scripts.py::TestSelect::test_re: passed != failed`
- `tests/test_scripts.py::TestSelect::test_reverse: passed != failed`
- `tests/test_scripts.py::TestSort::test_date: passed != failed`
- `tests/test_scripts.py::TestSort::test_default: passed != failed`
- `tests/test_scripts.py::TestSort::test_numeric: passed != failed`
- `tests/test_scripts.py::TestSort::test_reverse: passed != failed`
- `tests/test_scripts.py::TestSort::test_tags: passed != failed`
- `tests/test_scripts.py::TestTag::test_ambiguous: passed != failed`
- `tests/test_scripts.py::TestTag::test_default_tag: passed != failed`
- `tests/test_scripts.py::TestTag::test_full: passed != failed`
- `tests/test_scripts.py::TestTag::test_partial: passed != failed`
- `tests/test_scripts.py::TestTag::test_substrings: passed != failed`
- `tests/test_scripts.py::TestValidate::test_bad_hxl_status: passed != failed`
- `tests/test_scripts.py::TestValidate::test_default_invalid_status: passed != failed`
- `tests/test_scripts.py::TestValidate::test_default_valid_status: passed != failed`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_input.py::TestBadInput::test_bad_url: passed != failed`
- `tests/test_input.py::TestInput::test_ckan_dataset: passed != failed`
- `tests/test_input.py::TestInput::test_ckan_resource: passed != failed`
- `tests/test_input.py::TestInput::test_optional_params: passed != failed`
- `tests/test_input.py::TestParser::test_remote_csv: passed != failed`
- `tests/test_input.py::TestParser::test_remote_csv_hxl_ext: passed != failed`
- `tests/test_input.py::TestParser::test_remote_xls: passed != failed`
- `tests/test_input.py::TestParser::test_remote_xlsx: passed != failed`
- `tests/test_input.py::TestUntaggedInput::test_html: passed != failed`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
