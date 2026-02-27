"""
Sets up the environment variables for the action.
"""

from environs import Env


def get_env_vars(
    test: bool = False,
) -> tuple[
    str | None,
    list[str],
    int | None,
    int | None,
    bytes,
    bool,
    str | None,
    str,
    list[str],
    bool,
    str,
    str,
    str,
    bool,
]:
    """
    Get the environment variables for use in the action.

    Args:
        test (bool): Whether or not to load the environment variables from a .env file (default: False)

    Returns:
        organization (str | None): The organization to search for repositories in
        repository_list (list[str]): A list of repositories to search for
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for authentication
        gh_app_enterprise_only (bool): Set this to true if the GH APP is created on GHE and needs to communicate with GHE api only
        token (str | None): The GitHub token to use for authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        exempt_repositories_list (list[str]): A list of repositories to exempt from the action
        dry_run (bool): Whether or not to actually open issues/pull requests
        title (str): The title to use for the pull request
        body (str): The body to use for the pull request
        message (str): Commit message to use
        issue_report (bool): Whether or not to create an issue report with the results

    """
    env = Env()
    if not test:
        # Load from .env file if it exists
        env.read_env()

    organization = env.str("ORGANIZATION", default=None)
    repositories_str = env.str("REPOSITORY", default=None)
    # Either organization or repository must be set
    if not organization and not repositories_str:
        raise ValueError(
            "ORGANIZATION and REPOSITORY environment variables were not set. Please set one"
        )

    if repositories_str and repositories_str.find("/") == 0:
        raise ValueError(
            "REPOSITORY environment variable was not set correctly. Please set it to a comma separated list of repositories in the format org/repo"
        )

    # Separate repositories_str into a list based on the comma separator
    repositories_list = []
    if repositories_str:
        repositories_list = [
            repository.strip() for repository in repositories_str.split(",")
        ]

    gh_app_id = env.int("GH_APP_ID", default=None)
    gh_app_private_key_bytes = env.str("GH_APP_PRIVATE_KEY", default="").encode("utf8")
    gh_app_installation_id = env.int("GH_APP_INSTALLATION_ID", default=None)
    gh_app_enterprise_only = env.bool("GITHUB_APP_ENTERPRISE_ONLY", default=False)

    if gh_app_id and (not gh_app_private_key_bytes or not gh_app_installation_id):
        raise ValueError(
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set"
        )

    token = env.str("GH_TOKEN", default=None)
    if (
        not gh_app_id
        and not gh_app_private_key_bytes
        and not gh_app_installation_id
        and not token
    ):
        raise ValueError("GH_TOKEN environment variable not set")

    ghe = env.str("GH_ENTERPRISE_URL", default="").strip()

    exempt_repos = env.str("EXEMPT_REPOS", default=None)
    exempt_repositories_list = []
    if exempt_repos:
        exempt_repositories_list = [
            repository.strip() for repository in exempt_repos.split(",")
        ]

    dry_run = env.bool("DRY_RUN", default=False)

    title = env.str("TITLE", default=None)
    # make sure that title is a string with less than 70 characters
    if title:
        if len(title) > 70:
            raise ValueError(
                "TITLE environment variable is too long. Max 70 characters"
            )
    else:
        title = "Clean up CODEOWNERS file"

    body = env.str("BODY", default=None)
    # make sure that body is a string with less than 65536 characters
    if body:
        if len(body) > 65536:
            raise ValueError(
                "BODY environment variable is too long. Max 65536 characters"
            )
    else:
        body = "Consider these updates to the CODEOWNERS file to remove users no longer in this organization."

    commit_message = env.str("COMMIT_MESSAGE", default=None)
    if commit_message:
        if len(commit_message) > 65536:
            raise ValueError(
                "COMMIT_MESSAGE environment variable is too long. Max 65536 characters"
            )
    else:
        commit_message = (
            "Remove users no longer in this organization from CODEOWNERS file"
        )

    issue_report = env.bool("ISSUE_REPORT", default=False)

    return (
        organization,
        repositories_list,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        gh_app_enterprise_only,
        token,
        ghe,
        exempt_repositories_list,
        dry_run,
        title,
        body,
        commit_message,
        issue_report,
    )
