## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/capitalone@edgetest__dfc8b73c__click__typer/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 5 files
### migrating edgetest/interface.py
### migrating tests/test_integration_cfg.py
### migrating tests/test_integration_toml.py
### migrating tests/test_interface_cfg.py
### migrating tests/test_interface_toml.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_core.py::test_basic_setup: passed != not found`
- `tests/test_core.py::test_basic_setup_create_environment_error: passed != not found`
- `tests/test_core.py::test_basic_setup_lower_error: passed != not found`
- `tests/test_core.py::test_basic_setup_upgrade_error: passed != not found`
- `tests/test_core.py::test_init: passed != not found`
- `tests/test_core.py::test_run_tests: passed != not found`
- `tests/test_core.py::test_setup_extras: passed != not found`
- `tests/test_core.py::test_setup_pip_deps: passed != not found`
- `tests/test_core.py::test_setup_pip_deps_error: passed != not found`
- `tests/test_interface_cfg.py::test_cli_setup_extras_update: passed != not found`
- `tests/test_interface_cfg.py::test_cli_setup_reqs_update: passed != not found`
- `tests/test_interface_toml.py::test_cli_setup_extras_update: passed != not found`
- `tests/test_interface_toml.py::test_cli_setup_reqs_update: passed != not found`
- `tests/test_lib.py::test_create_environment: passed != not found`
- `tests/test_lib.py::test_path_to_python: passed != not found`
- `tests/test_lib.py::test_run_install_lower: passed != not found`
- `tests/test_lib.py::test_run_update: passed != not found`
- `tests/test_report.py::test_report: passed != not found`
- `tests/test_schema.py::test_add_envoption: passed != not found`
- `tests/test_schema.py::test_add_global_option: passed != not found`
- `tests/test_utils.py::test_convert_toml_array_to_string: passed != not found`
- `tests/test_utils.py::test_get_lower_bounds: passed != not found`
- `tests/test_utils.py::test_isin_case_dashhyphen_ins: passed != not found`
- `tests/test_utils.py::test_parse_cfg: passed != not found`
- `tests/test_utils.py::test_parse_cfg_default: passed != not found`
- `tests/test_utils.py::test_parse_cfg_reqs: passed != not found`
- `tests/test_utils.py::test_parse_cfg_reqs_default: passed != not found`
- `tests/test_utils.py::test_parse_custom_cfg: passed != not found`
- `tests/test_utils.py::test_parse_custom_toml: passed != not found`
- `tests/test_utils.py::test_parse_reqs: passed != not found`
- `tests/test_utils.py::test_parse_toml: passed != not found`
- `tests/test_utils.py::test_parse_toml_default: passed != not found`
- `tests/test_utils.py::test_parse_toml_reqs: passed != not found`
- `tests/test_utils.py::test_parse_toml_reqs_default: passed != not found`
- `tests/test_utils.py::test_upgrade_pyproject_toml: passed != not found`
- `tests/test_utils.py::test_upgrade_setup_cfg: passed != not found`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_core.py::test_basic_setup: passed != not found`
- `tests/test_core.py::test_basic_setup_create_environment_error: passed != not found`
- `tests/test_core.py::test_basic_setup_lower_error: passed != not found`
- `tests/test_core.py::test_basic_setup_upgrade_error: passed != not found`
- `tests/test_core.py::test_init: passed != not found`
- `tests/test_core.py::test_run_tests: passed != not found`
- `tests/test_core.py::test_setup_extras: passed != not found`
- `tests/test_core.py::test_setup_pip_deps: passed != not found`
- `tests/test_core.py::test_setup_pip_deps_error: passed != not found`
- `tests/test_interface_cfg.py::test_cli_setup_extras_update: passed != not found`
- `tests/test_interface_cfg.py::test_cli_setup_reqs_update: passed != not found`
- `tests/test_interface_toml.py::test_cli_setup_extras_update: passed != not found`
- `tests/test_interface_toml.py::test_cli_setup_reqs_update: passed != not found`
- `tests/test_lib.py::test_create_environment: passed != not found`
- `tests/test_lib.py::test_path_to_python: passed != not found`
- `tests/test_lib.py::test_run_install_lower: passed != not found`
- `tests/test_lib.py::test_run_update: passed != not found`
- `tests/test_report.py::test_report: passed != not found`
- `tests/test_schema.py::test_add_envoption: passed != not found`
- `tests/test_schema.py::test_add_global_option: passed != not found`
- `tests/test_utils.py::test_convert_toml_array_to_string: passed != not found`
- `tests/test_utils.py::test_get_lower_bounds: passed != not found`
- `tests/test_utils.py::test_isin_case_dashhyphen_ins: passed != not found`
- `tests/test_utils.py::test_parse_cfg: passed != not found`
- `tests/test_utils.py::test_parse_cfg_default: passed != not found`
- `tests/test_utils.py::test_parse_cfg_reqs: passed != not found`
- `tests/test_utils.py::test_parse_cfg_reqs_default: passed != not found`
- `tests/test_utils.py::test_parse_custom_cfg: passed != not found`
- `tests/test_utils.py::test_parse_custom_toml: passed != not found`
- `tests/test_utils.py::test_parse_reqs: passed != not found`
- `tests/test_utils.py::test_parse_toml: passed != not found`
- `tests/test_utils.py::test_parse_toml_default: passed != not found`
- `tests/test_utils.py::test_parse_toml_reqs: passed != not found`
- `tests/test_utils.py::test_parse_toml_reqs_default: passed != not found`
- `tests/test_utils.py::test_upgrade_pyproject_toml: passed != not found`
- `tests/test_utils.py::test_upgrade_setup_cfg: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
