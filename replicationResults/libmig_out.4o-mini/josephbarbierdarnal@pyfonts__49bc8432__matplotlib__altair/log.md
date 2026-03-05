## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/josephbarbierdarnal@pyfonts__49bc8432__matplotlib__altair/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 5 files
### migrating pyfonts/get_font.py
### migrating pyfonts/main.py
### migrating pyfonts/preview_font.py
### migrating tests/test_load_font.py
### migrating tests/test_preview_font.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_is_valid.py::test_is_url[-False]: passed != not found`
- `tests/test_is_valid.py::test_is_url[example.com-False]: passed != not found`
- `tests/test_is_valid.py::test_is_url[file:///C:/Users/username/Documents/file.txt-True]: passed != not found`
- `tests/test_is_valid.py::test_is_url[ftp://ftp.example.com-True]: passed != not found`
- `tests/test_is_valid.py::test_is_url[http://example.com-True]: passed != not found`
- `tests/test_is_valid.py::test_is_url[https://www.example.com-True]: passed != not found`
- `tests/test_is_valid.py::test_is_url[just a string-False]: passed != not found`
- `tests/test_is_valid.py::test_is_url[mailto:user@example.com-True]: passed != not found`
- `tests/test_is_valid.py::test_is_url[www.example.com-False]: passed != not found`
- `tests/test_is_valid.py::test_is_url_type_error: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://example.com/font.ttf-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://github.com/user/repo/blob/master/font.ttf-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://github.com/user/repo/blob/master/font.ttf?raw=false-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://github.com/user/repo/blob/master/font.ttf?raw=true&param=value-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://github.com/user/repo/blob/master/font.ttf?raw=true-True]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://github.com/user/repo/raw/master/font.WOFF-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://github.com/user/repo/raw/master/font.otf-True]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://github.com/user/repo/raw/master/font.txt-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://github.com/user/repo/tree/master/fonts/font.ttf-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://raw.githubusercontent.com/user/repo/branch-name/subfolder/font.woff2-True]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://raw.githubusercontent.com/user/repo/master/font.exe-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://raw.githubusercontent.com/user/repo/master/font.ttf?raw=true-False]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url[https://raw.githubusercontent.com/user/repo/master/font.woff-True]: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url_with_empty_string: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url_with_non_string: passed != not found`
- `tests/test_is_valid.py::test_is_valid_raw_url_with_none: passed != not found`
- `tests/test_load_font.py::test_load_font_invalid_input: passed != not found`
- `tests/test_load_font.py::test_load_font_no_input: passed != not found`
- `tests/test_load_font.py::test_load_font_with_path: passed != not found`
- `tests/test_load_font.py::test_load_font_with_url: passed != not found`
- `tests/test_preview_font.py::test_preview_font_raises_value_error_on_invalid_input: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/josephbarbierdarnal@pyfonts__49bc8432__matplotlib__altair/.venv
installing dependencies
