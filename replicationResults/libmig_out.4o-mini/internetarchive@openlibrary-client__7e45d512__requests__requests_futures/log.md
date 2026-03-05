## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/internetarchive@openlibrary-client__7e45d512__requests__requests_futures/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 3 files
### migrating olclient/entity_helpers/work.py
### migrating olclient/openlibrary.py
### migrating tests/test_openlibrary.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/schemata/test_import_schema.py::test_import_examples[example0]: passed != not found`
- `tests/schemata/test_import_schema.py::test_import_examples[example1]: passed != not found`
- `tests/schemata/test_import_schema.py::test_import_examples[example2]: passed != not found`
- `tests/test_book.py::TestBook::test_canonical_title: passed != not found`
- `tests/test_book.py::TestBook::test_create_book: passed != not found`
- `tests/test_book.py::TestBook::test_xisbn_to_books: passed != not found`
- `tests/test_bots.py::TestBots::test__init__: passed != not found`
- `tests/test_bots.py::TestBots::test__str2bool_errors_for_non_boolean_input: passed != not found`
- `tests/test_bots.py::TestBots::test__str2bool_returns_false_for_falsey_input: passed != not found`
- `tests/test_bots.py::TestBots::test__str2bool_returns_true_for_truthy_input: passed != not found`
- `tests/test_bots.py::TestBots::test_process_row_with_bytecode: passed != not found`
- `tests/test_bots.py::TestBots::test_process_row_with_string: passed != not found`
- `tests/test_bots.py::TestBots::test_save_exits_when_limit_reached: passed != not found`
- `tests/test_bots.py::TestBots::test_save_when_write_changes_is_false: passed != not found`
- `tests/test_bots.py::TestBots::test_save_when_write_changes_is_true: passed != not found`
- `tests/test_bots.py::TestBots::test_setup_logger: passed != not found`
- `tests/test_bots.py::TestBots::test_write_changes_declaration_when_write_changes_is_false: passed != not found`
- `tests/test_bots.py::TestBots::test_write_changes_declaration_when_write_changes_is_true: passed != not found`
- `tests/test_openlibrary.py::TestAuthors::test_author_validation: passed != not found`
- `tests/test_openlibrary.py::TestFullEditionGet::test_load_by_isbn: passed != not found`
- `tests/test_openlibrary.py::TestFullEditionGet::test_load_by_olid: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_create_book: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_delete: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_edition_json: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_edition_validation: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_get_edition_by_isbn: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_get_notfound: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_get_olid_by_isbn: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_get_olid_notfound_by_bibkey: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_get_work: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_get_work_by_metadata: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_matching_authors_olid: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_redirect: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_save_many: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_work_json: passed != not found`
- `tests/test_openlibrary.py::TestOpenLibrary::test_work_validation: passed != not found`
- `tests/test_openlibrary.py::TestTextType::test_edition_text_type: passed != not found`
- `tests/test_openlibrary.py::TestTextType::test_edition_text_type_from_string: passed != not found`
- `tests/test_openlibrary.py::TestTextType::test_work_text_type: passed != not found`
- `tests/test_openlibrary.py::TestTextType::test_work_text_type_from_string: passed != not found`
- `tests/test_utils.py::test_merge_unique_lists[input_0-merged0]: passed != not found`
- `tests/test_utils.py::test_merge_unique_lists[input_1-merged1]: passed != not found`
- `tests/test_utils.py::test_merge_unique_lists[input_2-merged2]: passed != not found`
- `tests/test_utils.py::test_merge_unique_lists[input_3-merged3]: passed != not found`
- `tests/test_utils.py::test_merge_unique_lists[input_4-merged4]: passed != not found`
- `tests/test_utils.py::test_merge_unique_lists[input_5-merged5]: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
