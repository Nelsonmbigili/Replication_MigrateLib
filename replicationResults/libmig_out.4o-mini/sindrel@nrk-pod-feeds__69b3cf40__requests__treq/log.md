## Running premig
creating venv at /Users/namugo/Desktop/대학대학/1. Spring 2026/CS-UH 3260 004 Software Analytics/Assignments/Replication 2/Replication_MigrateLib/repos/sindrel@nrk-pod-feeds__69b3cf40__requests__treq/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating common/psapi.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `common/test_psapi.py::test_get_all_podcast_episodes: passed != failed`
- `common/test_psapi.py::test_get_all_podcast_episodes_all_seasons: passed != failed`
- `common/test_psapi.py::test_get_all_podcasts: passed != failed`
- `common/test_psapi.py::test_get_episode_manifest: passed != failed`
- `common/test_psapi.py::test_get_podcast_episodes: passed != failed`
- `common/test_psapi.py::test_get_podcast_metadata: passed != failed`
- `test_discover_feeds.py::test_update_podcasts_config: passed != failed`
- `test_generate_feeds.py::test_get_podcast_void: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
