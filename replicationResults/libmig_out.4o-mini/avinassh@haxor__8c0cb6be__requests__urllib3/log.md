## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/avinassh@haxor__8c0cb6be__requests__urllib3/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 15 files
### migrating hackernews/__init__.py
### migrating tests/test_ask_stories.py
### migrating tests/test_get_async.py
### migrating tests/test_get_item.py
### migrating tests/test_get_items_by_ids.py
### migrating tests/test_get_last.py
### migrating tests/test_get_max_item.py
### migrating tests/test_get_sync.py
### migrating tests/test_get_user.py
### migrating tests/test_get_users_by_ids.py
### migrating tests/test_job_stories.py
### migrating tests/test_new_stories.py
### migrating tests/test_show_stories.py
### migrating tests/test_top_stories.py
### migrating tests/test_updates.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `tests/test_api_version.py::TestAPIVersion::test_invalid_api_version: passed != not found`
- `tests/test_api_version.py::TestAPIVersion::test_valid_api_version_1: passed != not found`
- `tests/test_api_version.py::TestAPIVersion::test_valid_api_version_2: passed != not found`
- `tests/test_ask_stories.py::TestAskStories::test_ask_stories: passed != not found`
- `tests/test_ask_stories.py::TestAskStories::test_ask_stories_raw: passed != not found`
- `tests/test_get_async.py::TestGetAsync::test_get_async: passed != not found`
- `tests/test_get_async.py::TestGetAsync::test_get_async_error: passed != not found`
- `tests/test_get_item.py::TestGetItem::test_get_item: passed != not found`
- `tests/test_get_item.py::TestGetItem::test_get_item_expand: passed != not found`
- `tests/test_get_item.py::TestGetItem::test_invalid_item: passed != not found`
- `tests/test_get_items_by_ids.py::TestGetItemsByIDs::test_get_items_by_ids: passed != not found`
- `tests/test_get_items_by_ids.py::TestGetItemsByIDs::test_get_items_by_ids_filtered: passed != not found`
- `tests/test_get_last.py::TestGetLast::test_get_item: passed != not found`
- `tests/test_get_max_item.py::TestGetMaxItem::test_get_max_item: passed != not found`
- `tests/test_get_max_item.py::TestGetMaxItem::test_get_max_item_expand: passed != not found`
- `tests/test_get_sync.py::TestGetSync::test_get_sync: passed != not found`
- `tests/test_get_sync.py::TestGetSync::test_get_sync_error: passed != not found`
- `tests/test_get_user.py::TestGetUser::test_get_invalid_user: passed != not found`
- `tests/test_get_user.py::TestGetUser::test_get_user: passed != not found`
- `tests/test_get_user.py::TestGetUser::test_get_user_expand: passed != not found`
- `tests/test_get_users_by_ids.py::TestGetUsersByIDs::test_get_users_by_ids: passed != not found`
- `tests/test_job_stories.py::TestJobStories::test_job_stories: passed != not found`
- `tests/test_job_stories.py::TestJobStories::test_job_stories_raw: passed != not found`
- `tests/test_new_stories.py::TestNewStories::test_new_stories: passed != not found`
- `tests/test_new_stories.py::TestNewStories::test_new_stories_raw: passed != not found`
- `tests/test_show_stories.py::TestShowStories::test_show_stories: passed != not found`
- `tests/test_show_stories.py::TestShowStories::test_show_stories_raw: passed != not found`
- `tests/test_top_stories.py::TestTopStories::test_top_stories: passed != not found`
- `tests/test_top_stories.py::TestTopStories::test_top_stories_raw: passed != not found`
- `tests/test_updates.py::TestUpdates::test_top_stories: passed != not found`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
- async_transform finished
