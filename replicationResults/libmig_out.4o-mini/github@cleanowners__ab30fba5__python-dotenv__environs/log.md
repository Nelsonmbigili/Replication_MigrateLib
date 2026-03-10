## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/github@cleanowners__ab30fba5__python-dotenv__environs/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating env.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `test_env.py::TestEnv::test_get_env_vars_auth_with_github_app_installation_missing_inputs: passed != failed`
- `test_env.py::TestEnv::test_get_env_vars_optional_values: passed != failed`
- `test_env.py::TestEnv::test_get_env_vars_with_org: passed != failed`
- `test_env.py::TestEnv::test_get_env_vars_with_repos_no_dry_run: passed != failed`
- `test_env.py::TestEnv::test_get_env_vars_with_token_and_repos: passed != failed`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_does_not_exist_and_default_value_returns_false: passed != failed`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_does_not_exist_and_default_value_returns_true: passed != failed`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_false: passed != failed`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_false_due_to_invalid_value: passed != failed`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_true: passed != failed`
- llmmig finished
## Running merge_skipped
### running tests
- test finished with status 2, cov finished with status 1
### test diff with round premig
- `test_auth.py::TestAuth::test_auth_to_github_invalid_credentials: passed != not found`
- `test_auth.py::TestAuth::test_auth_to_github_with_app: passed != not found`
- `test_auth.py::TestAuth::test_auth_to_github_with_ghe: passed != not found`
- `test_auth.py::TestAuth::test_auth_to_github_with_ghe_and_ghe_app: passed != not found`
- `test_auth.py::TestAuth::test_auth_to_github_with_token: passed != not found`
- `test_auth.py::TestAuth::test_auth_to_github_without_token: passed != not found`
- `test_cleanowners.py::TestCommitChanges::test_commit_changes: passed != not found`
- `test_cleanowners.py::TestGetCodeownersFile::test_codeowners_empty_file: passed != not found`
- `test_cleanowners.py::TestGetCodeownersFile::test_codeowners_in_docs_folder: passed != not found`
- `test_cleanowners.py::TestGetCodeownersFile::test_codeowners_in_github_folder: passed != not found`
- `test_cleanowners.py::TestGetCodeownersFile::test_codeowners_in_root: passed != not found`
- `test_cleanowners.py::TestGetCodeownersFile::test_codeowners_not_found: passed != not found`
- `test_cleanowners.py::TestGetOrganization::test_get_organization_fails: passed != not found`
- `test_cleanowners.py::TestGetOrganization::test_get_organization_succeeds: passed != not found`
- `test_cleanowners.py::TestGetReposIterator::test_get_repos_iterator_with_organization: passed != not found`
- `test_cleanowners.py::TestGetReposIterator::test_get_repos_iterator_with_repository_list: passed != not found`
- `test_cleanowners.py::TestGetUsernamesFromCodeowners::test_get_usernames_from_codeowners_ignore_teams: passed != not found`
- `test_cleanowners.py::TestGetUsernamesFromCodeowners::test_get_usernames_from_codeowners_with_teams: passed != not found`
- `test_cleanowners.py::TestPrintStats::test_print_stats_all_counts: passed != not found`
- `test_cleanowners.py::TestPrintStats::test_print_stats_no_pull_requests_needed: passed != not found`
- `test_cleanowners.py::TestPrintStats::test_print_stats_no_repositories_processed: passed != not found`
- `test_env.py::TestEnv::test_get_env_vars_auth_with_github_app_installation_missing_inputs: passed != not found`
- `test_env.py::TestEnv::test_get_env_vars_missing_org_or_repo: passed != not found`
- `test_env.py::TestEnv::test_get_env_vars_missing_token: passed != not found`
- `test_env.py::TestEnv::test_get_env_vars_optional_values: passed != not found`
- `test_env.py::TestEnv::test_get_env_vars_with_github_app_and_repos: passed != not found`
- `test_env.py::TestEnv::test_get_env_vars_with_org: passed != not found`
- `test_env.py::TestEnv::test_get_env_vars_with_repos_no_dry_run: passed != not found`
- `test_env.py::TestEnv::test_get_env_vars_with_token_and_repos: passed != not found`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_does_not_exist_and_default_value_returns_false: passed != not found`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_does_not_exist_and_default_value_returns_true: passed != not found`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_false: passed != not found`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_false_due_to_invalid_value: passed != not found`
- `test_env_get_bool.py::TestEnv::test_get_bool_env_var_that_exists_and_is_true: passed != not found`
- `test_markdown_writer.py::TestWriteToMarkdown::test_write_with_all_counts_and_no_users_to_remove: passed != not found`
- `test_markdown_writer.py::TestWriteToMarkdown::test_write_with_empty_inputs: passed != not found`
- `test_markdown_writer.py::TestWriteToMarkdown::test_write_with_repos_and_users_with_users_to_remove: passed != not found`
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
