## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/codewithemad@apyrat__de1852d8__requests__aiohttp/.venv
installing dependencies
### running tests
## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/codewithemad@apyrat__de1852d8__requests__aiohttp/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating apyrat/apyrat.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_apyrat.py::test_get_available_videos_single_video: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 10 functions to mark async including 6 tests
- Found 9 calls to await
- 4 files requires transformation
- transforming tests/test_apyrat.py
- transforming apyrat/cli.py
- transforming tests/cli_test.py
- transforming apyrat/apyrat.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `tests/test_apyrat.py::test_get_available_videos_single_video: passed != failed`
- async_transform finished
