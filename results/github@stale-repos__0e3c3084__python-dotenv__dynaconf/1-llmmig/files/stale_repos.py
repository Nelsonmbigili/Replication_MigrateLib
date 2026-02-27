#!/usr/bin/env python
""" Find stale repositories in a GitHub organization. """
import fnmatch
import json
from datetime import datetime, timezone
from os.path import dirname, join

import github3
from dateutil.parser import parse
from dynaconf import Dynaconf

# Initialize Dynaconf to load settings from .env and other sources
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[join(dirname(__file__), ".env")],
)


def main():  # pragma: no cover
    """
    Iterate over all repositories in the specified organization on GitHub,
    calculate the number of days since each repository was last pushed to,
    and print out the URL of any repository that has been inactive for more
    days than the specified threshold.

    The following environment variables must be set:
    - GH_TOKEN: a personal access token for the GitHub API
    - INACTIVE_DAYS: the number of days after which a repository is considered stale
    - ORGANIZATION: the name of the organization to search for repositories in

    If GH_ENTERPRISE_URL is set, the script will authenticate to a GitHub Enterprise
    instance instead of GitHub.com.
    """
    print("Starting stale repo search...")

    # Auth to GitHub.com
    github_connection = auth_to_github()

    # Set the threshold for inactive days
    inactive_days_threshold = settings.get("INACTIVE_DAYS")
    if not inactive_days_threshold:
        raise ValueError("INACTIVE_DAYS environment variable not set")

    # Set the organization
    organization = settings.get("ORGANIZATION")
    if not organization:
        print(
            "ORGANIZATION environment variable not set, searching all repos owned by token owner"
        )

    # Fetch additional metrics configuration
    additional_metrics = settings.get("ADDITIONAL_METRICS", "").split(",")

    # Iterate over repos in the org, acquire inactive days,
    # and print out the repo url and days inactive if it's over the threshold (inactive_days)
    inactive_repos = get_inactive_repos(
        github_connection, inactive_days_threshold, organization, additional_metrics
    )

    if inactive_repos:
        output_to_json(inactive_repos)
        write_to_markdown(inactive_repos, inactive_days_threshold, additional_metrics)
    else:
        print("No stale repos found")


def is_repo_exempt(repo, exempt_repos, exempt_topics):
    """Check if a repo is exempt from the stale repo check.

    Args:
        repo: The repository to check.
        exempt_repos: A list of repos to exempt from the stale repo check.
        exempt_topics: A list of topics to exempt from the stale repo check.

    Returns:
        True if the repo is exempt from the stale repo check, False otherwise.
    """
    if exempt_repos and any(
        fnmatch.fnmatchcase(repo.name, pattern) for pattern in exempt_repos
    ):
        print(f"{repo.html_url} is exempt from stale repo check")
        return True
    try:
        if exempt_topics and any(
            topic in exempt_topics for topic in repo.topics().names
        ):
            print(f"{repo.html_url} is exempt from stale repo check")
            return True
    except github3.exceptions.NotFoundError as error_code:
        if error_code.code == 404:
            print(
                f"{repo.html_url} does not have topics enabled and may be a private temporary fork"
            )

    return False


def get_inactive_repos(
    github_connection, inactive_days_threshold, organization, additional_metrics=None
):
    """Return and print out the repo url and days inactive if it's over
       the threshold (inactive_days).

    Args:
        github_connection: The GitHub connection object.
        inactive_days_threshold: The threshold (in days) for considering a repo as inactive.
        organization: The name of the organization to retrieve repositories from.
        additional_metrics: A list of additional metrics to include in the report.

    Returns:
        A list of tuples containing the repo, days inactive, the date of the last push and
        repository visibility (public/private).

    """
    inactive_repos = []
    if organization:
        repos = github_connection.organization(organization).repositories()
    else:
        repos = github_connection.repositories(type="owner")

    exempt_topics = settings.get("EXEMPT_TOPICS")
    if exempt_topics:
        exempt_topics = exempt_topics.replace(" ", "").split(",")
        print(f"Exempt topics: {exempt_topics}")

    exempt_repos = settings.get("EXEMPT_REPOS")
    if exempt_repos:
        exempt_repos = exempt_repos.replace(" ", "").split(",")
        print(f"Exempt repos: {exempt_repos}")

    for repo in repos:
        # check if repo is exempt from stale repo check
        if repo.archived:
            continue
        if is_repo_exempt(repo, exempt_repos, exempt_topics):
            continue

        # Get last active date
        active_date = get_active_date(repo)
        if active_date is None:
            continue

        active_date_disp = active_date.date().isoformat()
        days_inactive = (datetime.now(timezone.utc) - active_date).days
        visibility = "private" if repo.private else "public"
        if days_inactive > int(inactive_days_threshold):
            repo_data = set_repo_data(
                repo, days_inactive, active_date_disp, visibility, additional_metrics
            )
            inactive_repos.append(repo_data)
    if organization:
        print(f"Found {len(inactive_repos)} stale repos in {organization}")
    else:
        print(f"Found {len(inactive_repos)} stale repos")
    return inactive_repos


def get_active_date(repo):
    """Get the last activity date of the repository.

    Args:
        repo: A Github repository object.

    Returns:
        A date object representing the last activity date of the repository.
    """
    activity_method = settings.get("ACTIVITY_METHOD", "pushed").lower()
    try:
        if activity_method == "default_branch_updated":
            commit = repo.branch(repo.default_branch).commit
            active_date = parse(commit.commit.as_dict()["committer"]["date"])
        elif activity_method == "pushed":
            last_push_str = repo.pushed_at  # type: ignored
            if last_push_str is None:
                return None
            active_date = parse(last_push_str)
        else:
            raise ValueError(
                f"""
                ACTIVITY_METHOD environment variable has unsupported value: '{activity_method}'.
                Allowed values are: 'pushed' and 'default_branch_updated'
                """
            )
    except github3.exceptions.GitHubException:
        print(
            f"{repo.html_url} had an exception trying to get the activity date.\
 Potentially caused by ghost user."
        )
        return None
    return active_date


def auth_to_github():
    """Connect to GitHub.com or GitHub Enterprise, depending on env variables."""
    gh_app_id = settings.get("GH_APP_ID", cast=int)
    gh_app_private_key_bytes = settings.get("GH_APP_PRIVATE_KEY", "").encode("utf8")
    gh_app_installation_id = settings.get("GH_APP_INSTALLATION_ID", cast=int)
    ghe = settings.get("GH_ENTERPRISE_URL", default="").strip()
    token = settings.get("GH_TOKEN")

    if gh_app_id and gh_app_private_key_bytes and gh_app_installation_id:
        gh = github3.github.GitHub()
        gh.login_as_app_installation(
            gh_app_private_key_bytes, gh_app_id, gh_app_installation_id
        )
        github_connection = gh
    elif ghe and token:
        github_connection = github3.github.GitHubEnterprise(ghe, token=token)
    elif token:
        github_connection = github3.login(token=settings.get("GH_TOKEN"))
    else:
        raise ValueError("GH_TOKEN environment variable not set")

    if not github_connection:
        raise ValueError("Unable to authenticate to GitHub")
    return github_connection  # type: ignore


if __name__ == "__main__":
    main()
