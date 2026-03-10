## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/pelagicore@qface__4a77e9aa__jinja2__mako/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating qface/generator.py
### migrating qface/helper/qtcpp.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_climate.py::test_interface: passed != not found`
- `tests/test_comments.py::test_comment: passed != not found`
- `tests/test_comments.py::test_qdoc_translate: passed != not found`
- `tests/test_generator.py::test_destination_prefix: passed != not found`
- `tests/test_generator.py::test_error_template_doesnt_exist: passed != not found`
- `tests/test_generator.py::test_error_template_syntax_error: passed != not found`
- `tests/test_generator.py::test_error_template_undefined_variable: passed != not found`
- `tests/test_generator.py::test_error_yaml_doesnt_exist: passed != not found`
- `tests/test_generator.py::test_extra_filters: passed != not found`
- `tests/test_generator.py::test_gen_interface: passed != not found`
- `tests/test_generator.py::test_gen_module: passed != not found`
- `tests/test_generator.py::test_parse_document: passed != not found`
- `tests/test_generator.py::test_parse_document_list: passed != not found`
- `tests/test_generator.py::test_parse_document_mixed: passed != not found`
- `tests/test_generator.py::test_regeneration: passed != not found`
- `tests/test_generator.py::test_rulegenerator: passed != not found`
- `tests/test_json.py::test_echo_json: passed != not found`
- `tests/test_json.py::test_tuner_json: passed != not found`
- `tests/test_lookup.py::test_lookup: passed != not found`
- `tests/test_parser.py::test_default_values: passed != not found`
- `tests/test_parser.py::test_enum: passed != not found`
- `tests/test_parser.py::test_enum_counter: passed != not found`
- `tests/test_parser.py::test_extension: passed != not found`
- `tests/test_parser.py::test_flag: passed != not found`
- `tests/test_parser.py::test_flag_counter: passed != not found`
- `tests/test_parser.py::test_interface: passed != not found`
- `tests/test_parser.py::test_interface_property: passed != not found`
- `tests/test_parser.py::test_list: passed != not found`
- `tests/test_parser.py::test_map: passed != not found`
- `tests/test_parser.py::test_model: passed != not found`
- `tests/test_parser.py::test_module: passed != not found`
- `tests/test_parser.py::test_operation: passed != not found`
- `tests/test_parser.py::test_parse: passed != not found`
- `tests/test_parser.py::test_parser_exceptions: passed != not found`
- `tests/test_parser.py::test_property: passed != not found`
- `tests/test_parser.py::test_signals: passed != not found`
- `tests/test_parser.py::test_struct: passed != not found`
- `tests/test_parser.py::test_struct_list: passed != not found`
- `tests/test_parser.py::test_struct_map: passed != not found`
- `tests/test_parser.py::test_symbol_kind: passed != not found`
- `tests/test_qtcpp_helper.py::test_default_value: passed != not found`
- `tests/test_qtcpp_helper.py::test_namespace: passed != not found`
- `tests/test_qtcpp_helper.py::test_parameter_type: passed != not found`
- `tests/test_qtcpp_helper.py::test_return_type: passed != not found`
- `tests/test_tags.py::test_flag: passed != not found`
- `tests/test_tags.py::test_merge_annotation: passed != not found`
- `tests/test_tags.py::test_merge_broken_annotation: passed != not found`
- `tests/test_tags.py::test_merge_empty_annotation: passed != not found`
- `tests/test_tags.py::test_merge_invalid_annotation: passed != not found`
- `tests/test_tags.py::test_meta_tags: passed != not found`
- `tests/test_tags.py::test_tag: passed != not found`
- `tests/test_validation.py::test_resolve: passed != not found`
- `tests/test_validation.py::test_resolve_nested: passed != not found`
- `tests/test_values.py::test_values: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
