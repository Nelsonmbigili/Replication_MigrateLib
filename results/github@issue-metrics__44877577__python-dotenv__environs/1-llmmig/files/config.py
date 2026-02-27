"""A module for managing environment variables used in GitHub metrics calculation.

This module defines a class for encapsulating environment variables
and a function to retrieve these variables.

Classes:
    EnvVars: Represents the collection of environment variables used in the script.

Functions:
    get_env_vars: Retrieves and returns an instance of EnvVars populated with environment variables.
"""

from typing import List
from environs import Env


class EnvVars:
    # pylint: disable=too-many-instance-attributes
    """
    Environment variables

    Attributes:
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for
            authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for
            authentication
        gh_token (str | None): GitHub personal access token (PAT) for API authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        hide_author (bool): If true, the author's information is hidden in the output
        hide_items_closed_count (bool): If true, the number of items closed metric is hidden
            in the output
        hide_label_metrics (bool): If true, the label metrics are hidden in the output
        hide_time_to_answer (bool): If true, the time to answer discussions is hidden in the output
        hide_time_to_close (bool): If true, the time to close metric is hidden in the output
        hide_time_to_first_response (bool): If true, the time to first response metric is hidden
            in the output
        ignore_users (List[str]): List of usernames to ignore when calculating metrics
        labels_to_measure (List[str]): List of labels to measure how much time the label is applied
        enable_mentor_count (bool): If set to TRUE, compute number of mentors
        min_mentor_comments (str): If set, defines the minimum number of comments for mentors
        max_comments_eval (str): If set, defines the maximum number of comments to look
            at for mentor evaluation
        heavily_involved_cutoff (str): If set, defines the cutoff after which heavily
            involved commentors in
        search_query (str): Search query used to filter issues/prs/discussions on GitHub
        non_mentioning_links (bool): If set to TRUE, links do not cause a notification
            in the destination repository
        report_title (str): The title of the report
        output_file (str): The name of the file to write the report to
        rate_limit_bypass (bool): If set to TRUE, bypass the rate limit for the GitHub API
        draft_pr_tracking (bool): If set to TRUE, track PR time in draft state
            in addition to other metrics
    """

    def __init__(
        self,
        gh_app_id: int | None,
        gh_app_installation_id: int | None,
        gh_app_private_key_bytes: bytes,
        gh_app_enterprise_only: bool,
        gh_token: str | None,
        ghe: str | None,
        hide_author: bool,
        hide_items_closed_count: bool,
        hide_label_metrics: bool,
        hide_time_to_answer: bool,
        hide_time_to_close: bool,
        hide_time_to_first_response: bool,
        ignore_user: List[str],
        labels_to_measure: List[str],
        enable_mentor_count: bool,
        min_mentor_comments: str,
        max_comments_eval: str,
        heavily_involved_cutoff: str,
        search_query: str,
        non_mentioning_links: bool,
        report_title: str,
        output_file: str,
        rate_limit_bypass: bool = False,
        draft_pr_tracking: bool = False,
    ):
        self.gh_app_id = gh_app_id
        self.gh_app_installation_id = gh_app_installation_id
        self.gh_app_private_key_bytes = gh_app_private_key_bytes
        self.gh_app_enterprise_only = gh_app_enterprise_only
        self.gh_token = gh_token
        self.ghe = ghe
        self.ignore_users = ignore_user
        self.labels_to_measure = labels_to_measure
        self.hide_author = hide_author
        self.hide_items_closed_count = hide_items_closed_count
        self.hide_label_metrics = hide_label_metrics
        self.hide_time_to_answer = hide_time_to_answer
        self.hide_time_to_close = hide_time_to_close
        self.hide_time_to_first_response = hide_time_to_first_response
        self.enable_mentor_count = enable_mentor_count
        self.min_mentor_comments = min_mentor_comments
        self.max_comments_eval = max_comments_eval
        self.heavily_involved_cutoff = heavily_involved_cutoff
        self.search_query = search_query
        self.non_mentioning_links = non_mentioning_links
        self.report_title = report_title
        self.output_file = output_file
        self.rate_limit_bypass = rate_limit_bypass
        self.draft_pr_tracking = draft_pr_tracking

    def __repr__(self):
        return (
            f"EnvVars("
            f"{self.gh_app_id},"
            f"{self.gh_app_installation_id},"
            f"{self.gh_app_private_key_bytes},"
            f"{self.gh_app_enterprise_only},"
            f"{self.gh_token},"
            f"{self.ghe},"
            f"{self.hide_author},"
            f"{self.hide_items_closed_count}),"
            f"{self.hide_label_metrics},"
            f"{self.hide_time_to_answer},"
            f"{self.hide_time_to_close},"
            f"{self.hide_time_to_first_response},"
            f"{self.ignore_users},"
            f"{self.labels_to_measure},"
            f"{self.enable_mentor_count},"
            f"{self.min_mentor_comments},"
            f"{self.max_comments_eval},"
            f"{self.heavily_involved_cutoff},"
            f"{self.search_query}"
            f"{self.non_mentioning_links}"
            f"{self.report_title}"
            f"{self.output_file}"
            f"{self.rate_limit_bypass}"
            f"{self.draft_pr_tracking}"
        )


def get_env_vars(test: bool = False) -> EnvVars:
    """
    Get the environment variables for use in the script.

    Returns EnvVars object with all environment variables
    """
    env = Env()
    if not test:
        env.read_env()  # Automatically loads the .env file

    search_query = env.str("SEARCH_QUERY")
    gh_app_id = env.int("GH_APP_ID", default=None)
    gh_app_private_key_bytes = env.str("GH_APP_PRIVATE_KEY", default="").encode("utf8")
    gh_app_installation_id = env.int("GH_APP_INSTALLATION_ID", default=None)
    gh_app_enterprise_only = env.bool("GITHUB_APP_ENTERPRISE_ONLY", default=False)

    if gh_app_id and (not gh_app_private_key_bytes or not gh_app_installation_id):
        raise ValueError(
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set"
        )

    gh_token = env.str("GH_TOKEN", default=None)
    if (
        not gh_app_id
        and not gh_app_private_key_bytes
        and not gh_app_installation_id
        and not gh_token
    ):
        raise ValueError("GH_TOKEN environment variable not set")

    ghe = env.str("GH_ENTERPRISE_URL", default="").strip()

    labels_to_measure_list = env.list("LABELS_TO_MEASURE", default=[])
    ignore_users_list = env.list("IGNORE_USERS", default=[])

    report_title = env.str("REPORT_TITLE", "Issue Metrics")
    output_file = env.str("OUTPUT_FILE", "")
    rate_limit_bypass = env.bool("RATE_LIMIT_BYPASS", default=False)
    draft_pr_tracking = env.bool("DRAFT_PR_TRACKING", default=False)

    # Hidden columns
    hide_author = env.bool("HIDE_AUTHOR", default=False)
    hide_items_closed_count = env.bool("HIDE_ITEMS_CLOSED_COUNT", default=False)
    hide_label_metrics = env.bool("HIDE_LABEL_METRICS", default=False)
    hide_time_to_answer = env.bool("HIDE_TIME_TO_ANSWER", default=False)
    hide_time_to_close = env.bool("HIDE_TIME_TO_CLOSE", default=False)
    hide_time_to_first_response = env.bool("HIDE_TIME_TO_FIRST_RESPONSE", default=False)
    enable_mentor_count = env.bool("ENABLE_MENTOR_COUNT", default=False)
    min_mentor_comments = env.str("MIN_MENTOR_COMMENTS", default="10")
    max_comments_eval = env.str("MAX_COMMENTS_EVAL", default="20")
    heavily_involved_cutoff = env.str("HEAVILY_INVOLVED_CUTOFF", default="3")
    non_mentioning_links = env.bool("NON_MENTIONING_LINKS", default=False)

    return EnvVars(
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        gh_app_enterprise_only,
        gh_token,
        ghe,
        hide_author,
        hide_items_closed_count,
        hide_label_metrics,
        hide_time_to_answer,
        hide_time_to_close,
        hide_time_to_first_response,
        ignore_users_list,
        labels_to_measure_list,
        enable_mentor_count,
        min_mentor_comments,
        max_comments_eval,
        heavily_involved_cutoff,
        search_query,
        non_mentioning_links,
        report_title,
        output_file,
        rate_limit_bypass,
        draft_pr_tracking,
    )
