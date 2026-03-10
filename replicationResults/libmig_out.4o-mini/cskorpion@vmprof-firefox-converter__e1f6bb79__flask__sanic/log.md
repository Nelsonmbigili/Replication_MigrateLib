## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/cskorpion@vmprof-firefox-converter__e1f6bb79__flask__sanic/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating symbolserver/__init__.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `symbolserver/test/test_symbolserver.py::test_bc_to_str: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_code_dict_to_list: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_get_empty_jitlog_ir: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_get_example_ir_code: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_get_ir_code: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_get_jitlog_ir: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_get_mp_data: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_get_source_line: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_insert_code: passed != not found`
- `symbolserver/test/test_symbolserver.py::test_ir_to_str: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_jit_frame_not_mixed: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_jit_frame_to_mixed: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_lib: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_marker: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_native_frame: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_native_symbol: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_pypylog_interp_sample: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_pypylog_sample: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_resource: passed != not found`
- `vmprofconvert/test/test_convert.py::test_add_vmprof_frame: passed != not found`
- `vmprofconvert/test/test_convert.py::test_check_asm_frame: passed != not found`
- `vmprofconvert/test/test_convert.py::test_create_pypylog_marker: passed != not found`
- `vmprofconvert/test/test_convert.py::test_cut_pypylog: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dump_vmprof_meta: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dumps_filename_lines: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dumps_simple_profile: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dumps_vmprof: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dumps_vmprof_memory: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dumps_vmprof_no_lines: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dumps_vmprof_with_meta: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dumps_vmprof_with_pypylog: passed != not found`
- `vmprofconvert/test/test_convert.py::test_dumps_vmprof_without_pypylog: passed != not found`
- `vmprofconvert/test/test_convert.py::test_example: passed != not found`
- `vmprofconvert/test/test_convert.py::test_extract_files: passed != not found`
- `vmprofconvert/test/test_convert.py::test_filter_top_level_logs: passed != not found`
- `vmprofconvert/test/test_convert.py::test_frametable: passed != not found`
- `vmprofconvert/test/test_convert.py::test_functable: passed != not found`
- `vmprofconvert/test/test_convert.py::test_get_unused_tid: passed != not found`
- `vmprofconvert/test/test_convert.py::test_jit_asm_inline: passed != not found`
- `vmprofconvert/test/test_convert.py::test_load_zip_dict: passed != not found`
- `vmprofconvert/test/test_convert.py::test_multiple_threads: passed != not found`
- `vmprofconvert/test/test_convert.py::test_parse_pypylog: passed != not found`
- `vmprofconvert/test/test_convert.py::test_profiles: passed != not found`
- `vmprofconvert/test/test_convert.py::test_pypy_pystone: passed != not found`
- `vmprofconvert/test/test_convert.py::test_rescale_pypylog: passed != not found`
- `vmprofconvert/test/test_convert.py::test_sampleslist: passed != not found`
- `vmprofconvert/test/test_convert.py::test_save_zip: passed != not found`
- `vmprofconvert/test/test_convert.py::test_stacktable: passed != not found`
- `vmprofconvert/test/test_convert.py::test_stringarray: passed != not found`
- `vmprofconvert/test/test_convert.py::test_walk_full_pypylog: passed != not found`
- `vmprofconvert/test/test_convert.py::test_walk_pypylog: passed != not found`
- `vmprofconvert/test/test_convert.py::test_walk_pypylog_interpreter_samples: passed != not found`
- `vmprofconvert/test/test_convert.py::test_walk_pypylog_marker: passed != not found`
- `vmprofconvert/test/test_convert.py::test_walksample_vmprof: passed != not found`
- `vmprofconvert/test/test_convert.py::test_walksamples: passed != not found`
- `vmprofconvert/test/test_convert.py::test_write_file_dict: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
