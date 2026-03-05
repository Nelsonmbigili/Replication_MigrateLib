## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/chrispappalardo@eparse__6f799d21__click__typer/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating eparse/cli.py
### migrating tests/test_cli.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_cli.py::test_main: passed != not found`
- `tests/test_cli.py::test_migrate: passed != not found`
- `tests/test_cli.py::test_outputs: passed != not found`
- `tests/test_cli.py::test_parse: passed != not found`
- `tests/test_cli.py::test_query: passed != not found`
- `tests/test_cli.py::test_scan: passed != not found`
- `tests/test_core.py::test_df_find_tables: passed != not found`
- `tests/test_core.py::test_df_find_tables_loose: passed != not found`
- `tests/test_core.py::test_df_parse_table: passed != not found`
- `tests/test_core.py::test_df_parse_table_na_tolerance: passed != not found`
- `tests/test_core.py::test_df_serialize_table: passed != not found`
- `tests/test_core.py::test_get_df_from_file: passed != not found`
- `tests/test_core.py::test_get_table_digest: passed != not found`
- `tests/test_core.py::test_html_to_df_and_serialized_data: passed != not found`
- `tests/test_interfaces.py::test_ExcelParse_model: passed != not found`
- `tests/test_interfaces.py::test_html_interface: passed != not found`
- `tests/test_interfaces.py::test_null_interface: passed != not found`
- `tests/test_interfaces.py::test_parse_uri: passed != not found`
- `tests/test_interfaces.py::test_sqlite3_db: passed != not found`
- `tests/test_interfaces.py::test_sqlite3_interface: passed != not found`
- `tests/test_interfaces.py::test_stdout_interface: passed != not found`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_cli.py::test_main: passed != not found`
- `tests/test_cli.py::test_migrate: passed != not found`
- `tests/test_cli.py::test_outputs: passed != not found`
- `tests/test_cli.py::test_parse: passed != not found`
- `tests/test_cli.py::test_query: passed != not found`
- `tests/test_cli.py::test_scan: passed != not found`
- `tests/test_core.py::test_df_find_tables: passed != not found`
- `tests/test_core.py::test_df_find_tables_loose: passed != not found`
- `tests/test_core.py::test_df_parse_table: passed != not found`
- `tests/test_core.py::test_df_parse_table_na_tolerance: passed != not found`
- `tests/test_core.py::test_df_serialize_table: passed != not found`
- `tests/test_core.py::test_get_df_from_file: passed != not found`
- `tests/test_core.py::test_get_table_digest: passed != not found`
- `tests/test_core.py::test_html_to_df_and_serialized_data: passed != not found`
- `tests/test_interfaces.py::test_ExcelParse_model: passed != not found`
- `tests/test_interfaces.py::test_html_interface: passed != not found`
- `tests/test_interfaces.py::test_null_interface: passed != not found`
- `tests/test_interfaces.py::test_parse_uri: passed != not found`
- `tests/test_interfaces.py::test_sqlite3_db: passed != not found`
- `tests/test_interfaces.py::test_sqlite3_interface: passed != not found`
- `tests/test_interfaces.py::test_stdout_interface: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
