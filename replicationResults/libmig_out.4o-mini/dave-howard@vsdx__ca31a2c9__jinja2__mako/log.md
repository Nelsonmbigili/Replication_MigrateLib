## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/dave-howard@vsdx__ca31a2c9__jinja2__mako/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating vsdx/vsdxfile.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_jinja.py::test_basic_jinja[test_jinja.vsdx-context0]: passed != failed`
- `tests/test_jinja.py::test_basic_jinja[test_jinja.vsdx-context1]: passed != failed`
- `tests/test_jinja.py::test_basic_jinja[test_jinja.vsdx-context2]: passed != failed`
- `tests/test_jinja.py::test_basic_jinja_loop[test_jinja_loop.vsdx-context0]: passed != failed`
- `tests/test_jinja.py::test_basic_jinja_loop[test_jinja_loop.vsdx-context1]: passed != failed`
- `tests/test_jinja.py::test_basic_jinja_loop[test_jinja_loop.vsdx-context2]: passed != failed`
- `tests/test_jinja.py::test_jinja_calc[test_jinja.vsdx-context0]: passed != failed`
- `tests/test_jinja.py::test_jinja_calc[test_jinja.vsdx-context1]: passed != failed`
- `tests/test_jinja.py::test_jinja_calc[test_jinja.vsdx-context2]: passed != failed`
- `tests/test_jinja.py::test_jinja_if[test_jinja.vsdx-context0-1]: passed != failed`
- `tests/test_jinja.py::test_jinja_if[test_jinja.vsdx-context1-2]: passed != failed`
- `tests/test_jinja.py::test_jinja_if[test_jinja.vsdx-context2-3]: passed != failed`
- `tests/test_jinja.py::test_jinja_inner_loop[test_jinja_inner_loop.vsdx-context0]: passed != failed`
- `tests/test_jinja.py::test_jinja_inner_loop[test_jinja_inner_loop.vsdx-context1]: passed != failed`
- `tests/test_jinja.py::test_jinja_loop_showif[test_jinja_loop_showif.vsdx-1234-context0]: passed != failed`
- `tests/test_jinja.py::test_jinja_loop_showif[test_jinja_loop_showif.vsdx-3456-context1]: passed != failed`
- `tests/test_jinja.py::test_jinja_page_showif[test_jinja_page_showif.vsdx-context0-2-expected_page_names0]: passed != failed`
- `tests/test_jinja.py::test_jinja_page_showif[test_jinja_page_showif.vsdx-context1-2-expected_page_names1]: passed != failed`
- `tests/test_jinja.py::test_jinja_page_showif[test_jinja_page_showif.vsdx-context2-2-expected_page_names2]: passed != failed`
- `tests/test_jinja.py::test_jinja_page_showif[test_jinja_page_showif.vsdx-context3-2-expected_page_names3]: passed != failed`
- `tests/test_jinja.py::test_jinja_page_showif[test_jinja_page_showif.vsdx-context4-2-expected_page_names4]: passed != failed`
- `tests/test_jinja.py::test_jinja_page_showif[test_jinja_page_showif.vsdx-context5-2-expected_page_names5]: passed != failed`
- `tests/test_jinja.py::test_jinja_page_showif[test_jinja_page_showif.vsdx-context6-2-expected_page_names6]: passed != failed`
- `tests/test_jinja.py::test_jinja_self_ref_calculations[test_jinja_self_refs.vsdx-context0-4-10.12368731806121-This shape should move down by 1.0\n]: passed != failed`
- `tests/test_jinja.py::test_jinja_self_ref_calculations[test_jinja_self_refs.vsdx-context1-5-8.726049539918966-This shape should move down by n\n]: passed != failed`
- `tests/test_jinja.py::test_jinja_self_ref_calculations[test_jinja_self_refs.vsdx-context2-5-7.726049539918966-This shape should move down by n\n]: passed != failed`
- `tests/test_jinja.py::test_jinja_self_refs[test_jinja_self_refs.vsdx-context0-1-2.0-This text should remain  and x should be 2.0\n]: passed != failed`
- `tests/test_jinja.py::test_jinja_self_refs[test_jinja_self_refs.vsdx-context1-2-4.0-This shape sets x to n * 2\n]: passed != failed`
- `tests/test_jinja.py::test_jinja_self_refs[test_jinja_self_refs.vsdx-context2-3-1.0-This shape sets x to 1 if n else 2\n]: passed != failed`
- `tests/test_jinja.py::test_jinja_self_refs[test_jinja_self_refs.vsdx-context3-3-2.0-This shape sets x to 1 if n else 2\n]: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
