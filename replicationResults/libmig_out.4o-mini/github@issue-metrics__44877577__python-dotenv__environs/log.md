## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/github@issue-metrics__44877577__python-dotenv__environs/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating config.py
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test_auth.py::TestAuthToGithub::test_auth_to_github_invalid_credentials: passed != not found`
- `test_auth.py::TestAuthToGithub::test_auth_to_github_with_ghe: passed != not found`
- `test_auth.py::TestAuthToGithub::test_auth_to_github_with_ghe_and_ghe_app: passed != not found`
- `test_auth.py::TestAuthToGithub::test_auth_to_github_with_github_app: passed != not found`
- `test_auth.py::TestAuthToGithub::test_auth_to_github_with_token: passed != not found`
- `test_auth.py::TestAuthToGithub::test_auth_to_github_without_authentication_information: passed != not found`
- `test_auth.py::TestAuthToGithub::test_get_github_app_installation_token: passed != not found`
- `test_auth.py::TestAuthToGithub::test_get_github_app_installation_token_request_failure: passed != not found`
- `test_config.py::TestGetEnvVars::test_get_env_vars_auth_with_github_app_installation_missing_inputs: passed != not found`
- `test_config.py::TestGetEnvVars::test_get_env_vars_missing_query: passed != not found`
- `test_config.py::TestGetEnvVars::test_get_env_vars_missing_token: passed != not found`
- `test_config.py::TestGetEnvVars::test_get_env_vars_optional_values: passed != not found`
- `test_config.py::TestGetEnvVars::test_get_env_vars_optionals_are_defaulted: passed != not found`
- `test_config.py::TestGetEnvVars::test_get_env_vars_with_github_app: passed != not found`
- `test_config.py::TestGetEnvVars::test_get_env_vars_with_token: passed != not found`
- `test_config.py::TestGetIntFromEnv::test_get_int_env_var: passed != not found`
- `test_config.py::TestGetIntFromEnv::test_get_int_env_var_with_empty_env_var: passed != not found`
- `test_config.py::TestGetIntFromEnv::test_get_int_env_var_with_non_integer: passed != not found`
- `test_config_get_bool.py::TestEnv::test_get_bool_env_var_that_does_not_exist_and_default_value_returns_false: passed != not found`
- `test_config_get_bool.py::TestEnv::test_get_bool_env_var_that_does_not_exist_and_default_value_returns_true: passed != not found`
- `test_config_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_false: passed != not found`
- `test_config_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_false_due_to_invalid_value: passed != not found`
- `test_config_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_true: passed != not found`
- `test_discussions.py::TestGetDiscussions::test_get_discussions_error_status_code: passed != not found`
- `test_discussions.py::TestGetDiscussions::test_get_discussions_graphql_error: passed != not found`
- `test_discussions.py::TestGetDiscussions::test_get_discussions_multiple_pages: passed != not found`
- `test_discussions.py::TestGetDiscussions::test_get_discussions_single_page: passed != not found`
- `test_issue_metrics.py::TestDiscussionMetrics::test_get_per_issue_metrics_with_discussion: passed != not found`
- `test_issue_metrics.py::TestDiscussionMetrics::test_get_per_issue_metrics_with_discussion_with_hide_envs: passed != not found`
- `test_issue_metrics.py::TestGetEnvVars::test_get_env_vars: passed != not found`
- `test_issue_metrics.py::TestGetEnvVars::test_get_env_vars_missing_query: passed != not found`
- `test_issue_metrics.py::TestGetPerIssueMetrics::test_get_per_issue_metrics_with_hide_envs: passed != not found`
- `test_issue_metrics.py::TestGetPerIssueMetrics::test_get_per_issue_metrics_with_ignore_users: passed != not found`
- `test_issue_metrics.py::TestGetPerIssueMetrics::test_get_per_issue_metrics_without_hide_envs: passed != not found`
- `test_json_writer.py::TestWriteToJson::test_write_to_json: passed != not found`
- `test_json_writer.py::TestWriteToJson::test_write_to_json_with_no_response: passed != not found`
- `test_labels.py::TestGetAverageTimeInLabels::test_get_stats_time_in_labels: passed != not found`
- `test_labels.py::TestLabels::test_get_label_events: passed != not found`
- `test_labels.py::TestLabels::test_get_label_metrics_closed_issue: passed != not found`
- `test_labels.py::TestLabels::test_get_label_metrics_closed_issue_labeled_past_closed_at: passed != not found`
- `test_labels.py::TestLabels::test_get_label_metrics_open_issue: passed != not found`
- `test_markdown_helpers.py::TestMarkdownHelpers::test_markdown_too_large_for_issue_body: passed != not found`
- `test_markdown_helpers.py::TestMarkdownHelpers::test_split_markdown_file: passed != not found`
- `test_markdown_writer.py::TestWriteToMarkdown::test_write_to_markdown: passed != not found`
- `test_markdown_writer.py::TestWriteToMarkdown::test_write_to_markdown_no_issues: passed != not found`
- `test_markdown_writer.py::TestWriteToMarkdown::test_write_to_markdown_with_vertical_bar_in_title: passed != not found`
- `test_markdown_writer.py::TestWriteToMarkdownWithEnv::test_writes_markdown_file_with_non_hidden_columns_only: passed != not found`
- `test_most_active_mentors.py::TestCountCommentsPerUser::test_count_comments_per_user_limit: passed != not found`
- `test_most_active_mentors.py::TestCountCommentsPerUser::test_count_comments_per_user_with_ignores: passed != not found`
- `test_most_active_mentors.py::TestCountCommentsPerUser::test_get_mentor_count: passed != not found`
- `test_search.py::TestGetOwnerAndRepository::test_get_owner_and_repositories_without_repo_in_query: passed != not found`
- `test_search.py::TestGetOwnerAndRepository::test_get_owners_and_repositories_with_multiple_entries: passed != not found`
- `test_search.py::TestGetOwnerAndRepository::test_get_owners_and_repositories_with_org: passed != not found`
- `test_search.py::TestGetOwnerAndRepository::test_get_owners_and_repositories_with_user: passed != not found`
- `test_search.py::TestGetOwnerAndRepository::test_get_owners_and_repositories_without_either_in_query: passed != not found`
- `test_search.py::TestGetOwnerAndRepository::test_get_owners_with_owner_and_repo_in_query: passed != not found`
- `test_search.py::TestSearchIssues::test_search_issues_with_just_owner_or_org: passed != not found`
- `test_search.py::TestSearchIssues::test_search_issues_with_just_owner_or_org_with_bypass: passed != not found`
- `test_search.py::TestSearchIssues::test_search_issues_with_owner_and_repository: passed != not found`
- `test_time_in_draft.py::TestGetStatsTimeInDraft::test_get_stats_time_in_draft_empty_list: passed != not found`
- `test_time_in_draft.py::TestGetStatsTimeInDraft::test_get_stats_time_in_draft_no_data: passed != not found`
- `test_time_in_draft.py::TestGetStatsTimeInDraft::test_get_stats_time_in_draft_with_data: passed != not found`
- `test_time_in_draft.py::TestMeasureTimeInDraft::test_time_in_draft_multiple_intervals: passed != not found`
- `test_time_in_draft.py::TestMeasureTimeInDraft::test_time_in_draft_no_draft_events: passed != not found`
- `test_time_in_draft.py::TestMeasureTimeInDraft::test_time_in_draft_ongoing_draft: passed != not found`
- `test_time_in_draft.py::TestMeasureTimeInDraft::test_time_in_draft_with_ready_for_review: passed != not found`
- `test_time_in_draft.py::TestMeasureTimeInDraft::test_time_in_draft_without_ready_for_review: passed != not found`
- `test_time_in_draft.py::TestMeasureTimeInDraft::test_time_in_draft_without_ready_for_review_and_closed: passed != not found`
- `test_time_to_answer.py::TestGetAverageTimeToAnswer::test_returns_none_for_empty_list: passed != not found`
- `test_time_to_answer.py::TestGetAverageTimeToAnswer::test_returns_none_for_list_with_no_time_to_answer: passed != not found`
- `test_time_to_answer.py::TestGetAverageTimeToAnswer::test_returns_stats_time_to_answer: passed != not found`
- `test_time_to_answer.py::TestMeasureTimeToAnswer::test_returns_none_if_answer_chosen_at_is_missing: passed != not found`
- `test_time_to_answer.py::TestMeasureTimeToAnswer::test_returns_none_if_created_at_is_missing: passed != not found`
- `test_time_to_answer.py::TestMeasureTimeToAnswer::test_returns_time_to_answer: passed != not found`
- `test_time_to_close.py::TestGetAverageTimeToClose::test_get_stats_time_to_close: passed != not found`
- `test_time_to_close.py::TestGetAverageTimeToClose::test_get_stats_time_to_close_no_issues: passed != not found`
- `test_time_to_close.py::TestMeasureTimeToClose::test_measure_time_to_close: passed != not found`
- `test_time_to_close.py::TestMeasureTimeToClose::test_measure_time_to_close_discussion: passed != not found`
- `test_time_to_close.py::TestMeasureTimeToClose::test_measure_time_to_close_returns_none: passed != not found`
- `test_time_to_first_response.py::TestGetStatsTimeToFirstResponse::test_get_stats_time_to_first_response: passed != not found`
- `test_time_to_first_response.py::TestGetStatsTimeToFirstResponse::test_get_stats_time_to_first_response_with_all_none: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_ignore_bot: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_ignore_issue_owners_comment: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_ignore_pending_review: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_ignore_users: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_issue_comment_faster: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_no_comments: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_only_ignored_users: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_pull_request_comment_faster: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_pull_request_comment_ignore_before_ready: passed != not found`
- `test_time_to_first_response.py::TestMeasureTimeToFirstResponse::test_measure_time_to_first_response_with_pull_request_comments: passed != not found`
- `test_time_to_merge.py::TestMeasureTimeToMerge::test_measure_time_to_merge_created_at: passed != not found`
- `test_time_to_merge.py::TestMeasureTimeToMerge::test_measure_time_to_merge_ready_for_review: passed != not found`
- `test_time_to_merge.py::TestMeasureTimeToMerge::test_measure_time_to_merge_returns_none: passed != not found`
- `test_time_to_ready_for_review.py::TestGetTimeToReadyForReview::test_get_time_to_ready_for_review_event: passed != not found`
- `test_time_to_ready_for_review.py::TestGetTimeToReadyForReview::test_get_time_to_ready_for_review_no_event: passed != not found`
- `test_time_to_ready_for_review.py::TestGetTimeToReadyForReview::test_time_to_ready_for_review_draft: passed != not found`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `test_config.py::TestGetEnvVars::test_get_env_vars_auth_with_github_app_installation_missing_inputs: passed != failed`
- `test_config.py::TestGetEnvVars::test_get_env_vars_optional_values: passed != failed`
- `test_config.py::TestGetEnvVars::test_get_env_vars_optionals_are_defaulted: passed != failed`
- `test_config.py::TestGetEnvVars::test_get_env_vars_with_github_app: passed != failed`
- `test_config.py::TestGetEnvVars::test_get_env_vars_with_token: passed != failed`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
