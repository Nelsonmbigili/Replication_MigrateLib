## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/joeyagreco@sleeper__f5beb770__requests__treq/.venv
installing dependencies
### running tests
- test finished with status 1, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 2 files
### migrating sleeper/api/_utils.py
### migrating test/unit/helper/helper_classes.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `test/integration/test_api/test_avatar.py::TestAvatar::test_get_avatar_as_thumbnail: passed != failed`
- `test/integration/test_api/test_avatar.py::TestAvatar::test_get_avatar_defaults: passed != failed`
- `test/integration/test_api/test_draft.py::TestDraft::test_get_draft: passed != failed`
- `test/integration/test_api/test_draft.py::TestDraft::test_get_drafts_in_league: passed != failed`
- `test/integration/test_api/test_draft.py::TestDraft::test_get_player_draft_picks: passed != failed`
- `test/integration/test_api/test_draft.py::TestDraft::test_get_traded_draft_picks: passed != failed`
- `test/integration/test_api/test_draft.py::TestDraft::test_get_user_drafts_for_year_happy_path: passed != failed`
- `test/integration/test_api/test_league.py::TestLeague::test_get_losers_bracket: passed != failed`
- `test/integration/test_api/test_league.py::TestLeague::test_get_matchups_for_week: passed != failed`
- `test/integration/test_api/test_league.py::TestLeague::test_get_rosters: passed != failed`
- `test/integration/test_api/test_league.py::TestLeague::test_get_sport_state: passed != failed`
- `test/integration/test_api/test_league.py::TestLeague::test_get_traded_picks: passed != failed`
- `test/integration/test_api/test_league.py::TestLeague::test_get_transactions: passed != failed`
- `test/integration/test_api/test_league.py::TestLeague::test_get_users_in_league: passed != failed`
- `test/integration/test_api/test_league.py::TestLeague::test_get_winners_bracket: passed != failed`
- `test/integration/test_api/test_player.py::TestPlayer::test_get_all_players: passed != failed`
- `test/integration/test_api/test_player.py::TestPlayer::test_get_trending_players: passed != failed`
- `test/integration/test_api/test_user.py::TestUser::test_get_user_with_user_id_as_identifier: passed != failed`
- `test/integration/test_api/test_user.py::TestUser::test_get_user_with_username_as_identifier: passed != failed`
- `test/unit/test_api/test_avatar.py::TestAvatar::test_get_avatar_as_thumbnail: passed != failed`
- `test/unit/test_api/test_avatar.py::TestAvatar::test_get_avatar_defaults: passed != failed`
- `test/unit/test_api/test_draft.py::TestDraft::test_get_draft: passed != failed`
- `test/unit/test_api/test_draft.py::TestDraft::test_get_drafts_in_league: passed != failed`
- `test/unit/test_api/test_draft.py::TestDraft::test_get_player_draft_picks: passed != failed`
- `test/unit/test_api/test_draft.py::TestDraft::test_get_traded_draft_picks: passed != failed`
- `test/unit/test_api/test_draft.py::TestDraft::test_get_user_drafts_for_year_happy_path: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_league: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_losers_bracket: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_matchups_for_week: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_rosters: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_sport_state: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_traded_picks: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_transactions: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_user_leagues_for_year: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_users_in_league: passed != failed`
- `test/unit/test_api/test_league.py::TestLeague::test_get_winners_bracket: passed != failed`
- `test/unit/test_api/test_player.py::TestPlayer::test_get_all_players: passed != failed`
- `test/unit/test_api/test_player.py::TestPlayer::test_get_trending_players_with_defaults: passed != failed`
- `test/unit/test_api/test_player.py::TestPlayer::test_get_trending_players_with_optional_params_given: passed != failed`
- `test/unit/test_api/test_user.py::TestUser::test_get_user: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
