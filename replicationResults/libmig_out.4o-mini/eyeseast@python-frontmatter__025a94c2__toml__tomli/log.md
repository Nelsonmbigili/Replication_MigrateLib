## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/eyeseast@python-frontmatter__025a94c2__toml__tomli/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating frontmatter/default_handlers.py
### migrating tests/unit_test.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_docs.py::test_api_docs: passed != not found`
- `tests/test_docs.py::test_handler_docs: passed != not found`
- `tests/test_docs.py::test_readme: passed != not found`
- `tests/test_files.py::test_can_parse[filename0]: passed != not found`
- `tests/test_files.py::test_can_parse[filename10]: passed != not found`
- `tests/test_files.py::test_can_parse[filename1]: passed != not found`
- `tests/test_files.py::test_can_parse[filename2]: passed != not found`
- `tests/test_files.py::test_can_parse[filename3]: passed != not found`
- `tests/test_files.py::test_can_parse[filename4]: passed != not found`
- `tests/test_files.py::test_can_parse[filename5]: passed != not found`
- `tests/test_files.py::test_can_parse[filename6]: passed != not found`
- `tests/test_files.py::test_can_parse[filename7]: passed != not found`
- `tests/test_files.py::test_can_parse[filename8]: passed != not found`
- `tests/test_files.py::test_can_parse[filename9]: passed != not found`
- `tests/test_files.py::test_file[filename0]: passed != not found`
- `tests/test_files.py::test_file[filename10]: passed != not found`
- `tests/test_files.py::test_file[filename1]: passed != not found`
- `tests/test_files.py::test_file[filename2]: passed != not found`
- `tests/test_files.py::test_file[filename3]: passed != not found`
- `tests/test_files.py::test_file[filename4]: passed != not found`
- `tests/test_files.py::test_file[filename5]: passed != not found`
- `tests/test_files.py::test_file[filename6]: passed != not found`
- `tests/test_files.py::test_file[filename7]: passed != not found`
- `tests/test_files.py::test_file[filename8]: passed != not found`
- `tests/test_files.py::test_file[filename9]: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_check_empty_frontmatter: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_check_no_frontmatter: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_dump_to_file: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_dumping_with_custom_delimiters: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_empty_frontmatter: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_extra_space: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_no_frontmatter: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_pretty_dumping: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_to_dict: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_to_string: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_unicode_post: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_with_crlf_string: passed != not found`
- `tests/unit_test.py::FrontmatterTest::test_with_markdown_content: passed != not found`
- `tests/unit_test.py::HandlerTest::test_custom_handler: passed != not found`
- `tests/unit_test.py::HandlerTest::test_detect_format: passed != not found`
- `tests/unit_test.py::HandlerTest::test_json: passed != not found`
- `tests/unit_test.py::HandlerTest::test_no_handler: passed != not found`
- `tests/unit_test.py::HandlerTest::test_sanity_all: passed != not found`
- `tests/unit_test.py::HandlerTest::test_toml: passed != not found`
- `tests/unit_test.py::JSONHandlerTest::test_detect: passed != not found`
- `tests/unit_test.py::JSONHandlerTest::test_external: passed != not found`
- `tests/unit_test.py::JSONHandlerTest::test_split_content: passed != not found`
- `tests/unit_test.py::JSONHandlerTest::test_split_load: passed != not found`
- `tests/unit_test.py::TOMLHandlerTest::test_detect: passed != not found`
- `tests/unit_test.py::TOMLHandlerTest::test_external: passed != not found`
- `tests/unit_test.py::TOMLHandlerTest::test_split_content: passed != not found`
- `tests/unit_test.py::TOMLHandlerTest::test_split_load: passed != not found`
- `tests/unit_test.py::YAMLHandlerTest::test_detect: passed != not found`
- `tests/unit_test.py::YAMLHandlerTest::test_external: passed != not found`
- `tests/unit_test.py::YAMLHandlerTest::test_split_content: passed != not found`
- `tests/unit_test.py::YAMLHandlerTest::test_split_load: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
