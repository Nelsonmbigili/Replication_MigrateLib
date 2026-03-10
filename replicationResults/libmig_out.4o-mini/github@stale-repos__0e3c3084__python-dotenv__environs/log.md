## Running premig
creating venv at /Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/migratelib-artifact/repos/github@stale-repos__0e3c3084__python-dotenv__environs/.venv
installing dependencies
### running tests
- test finished with status 0, cov finished with status 0
## Running llmmig
## starting llmmig round
- migrating 1 files
### migrating stale_repos.py
### running tests
- test finished with status 1, cov finished with status 0
### test diff with round premig
- `test_stale_repos.py::AuthToGithubTestCase::test_auth_to_github_app_with_github_app_installation_env_vars: passed != failed`
- `test_stale_repos.py::AuthToGithubTestCase::test_auth_to_github_authentication_failure: passed != failed`
- `test_stale_repos.py::AuthToGithubTestCase::test_auth_to_github_with_enterprise_url_and_token: passed != failed`
- `test_stale_repos.py::AuthToGithubTestCase::test_auth_to_github_with_token: passed != failed`
- `test_stale_repos.py::AuthToGithubTestCase::test_auth_to_github_without_enterprise_url: passed != failed`
- `test_stale_repos.py::AuthToGithubTestCase::test_auth_to_github_without_environment_variables: passed != failed`
- `test_stale_repos.py::GetActiveDateTestCase::test_returns_none_for_exception: passed != failed`
- `test_stale_repos.py::GetInactiveReposTestCase::test_get_inactive_repos_with_default_branch_updated: passed != failed`
- `test_stale_repos.py::GetInactiveReposTestCase::test_get_inactive_repos_with_exempt_topics: passed != failed`
- `test_stale_repos.py::GetInactiveReposTestCase::test_get_inactive_repos_with_inactive_repos: passed != failed`
- `test_stale_repos.py::GetInactiveReposTestCase::test_get_inactive_repos_with_no_inactive_repos: passed != failed`
- `test_stale_repos.py::GetInactiveReposTestCase::test_get_inactive_repos_with_no_organization_set: passed != failed`
- `test_stale_repos.py::TestAdditionalMetrics::test_report_exclusion_with_additional_metrics_not_configured: passed != failed`
- `test_stale_repos.py::TestAdditionalMetrics::test_report_inclusion_with_additional_metrics_configured: passed != failed`
- `test_stale_repos.py::TestGetIntFromEnv::test_get_int_env_var: passed != failed`
- `test_stale_repos.py::TestGetIntFromEnv::test_get_int_env_var_with_empty_env_var: passed != failed`
- `test_stale_repos.py::TestGetIntFromEnv::test_get_int_env_var_with_non_integer: passed != failed`
- llmmig finished
## Running merge_skipped
- merge_skipped finished
## Running async_transform
## Running inferred async transform
### Finding async transforms
- Found 0 functions to mark async including 0 tests
- Found 0 calls to await
- async_transform finished
