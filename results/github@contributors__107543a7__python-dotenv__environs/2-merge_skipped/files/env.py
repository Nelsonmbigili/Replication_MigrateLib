"""
A GitHub Action that given an organization or repository,
produces information about the contributors over the specified time period.
"""

import datetime
from environs import Env

env = Env()
from dotenv import load_dotenv


def get_bool_env_var(env_var_name: str, default: bool = False) -> bool:
    """Get a boolean environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.
        default: The default value to return if the environment variable is not set.

    Returns:
        The value of the environment variable as a boolean.
    """
    ev = os.environ.get(env_var_name, "")
    if ev == "" and default:
        return default
    return ev.strip().lower() == "true"


def get_int_env_var(env_var_name: str) -> int | None:
    """Get an integer environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.

    Returns:
        The value of the environment variable as an integer or None.
    """
    env_var = os.environ.get(env_var_name)
    if env_var is None or not env_var.strip():
        return None
    try:
        return int(env_var)
    except ValueError:
        return None
env.read_env()  # Automatically reads the .env file


def validate_date_format(env_var_name: str) -> str:
    """Validate the date format of the environment variable.

    Does nothing if the environment variable is not set.

    Args:
        env_var_name: The name of the environment variable to retrieve.

    Returns:
        The value of the environment variable as a string.
    """
    date_to_validate = env.str(env_var_name, default="")

    if not date_to_validate:
        return date_to_validate

    pattern = "%Y-%m-%d"
    try:
        datetime.datetime.strptime(date_to_validate, pattern)
    except ValueError as exc:
        raise ValueError(
            f"{env_var_name} environment variable not in the format YYYY-MM-DD"
        ) from exc
    return date_to_validate


def get_env_vars(
    test: bool = False,
) -> tuple[
    str | None,
    list[str],
    int | None,
    int | None,
    bytes,
    bool,
    str,
    str,
    str,
    str,
    bool,
    bool,
]:
    """
    Get the environment variables for use in the action.

    Args:
        None

    Returns:
        organization (str): the organization to get contributor information for
        repository_list (list[str]): A list of the repositories to get contributor information for
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for authentication
        gh_app_enterprise_only (bool): Set this to true if the GH APP is created on GHE and needs to communicate with GHE api only
        token (str): The GitHub token to use for authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        start_date (str): The start date to get contributor information from
        end_date (str): The end date to get contributor information to.
        sponsor_info (str): Whether to get sponsor information on the contributor
        link_to_profile (str): Whether to link username to Github profile in markdown output
    """

    if not test:
        env.read_env()  # Load environment variables from .env file

    organization = env.str("ORGANIZATION", default=None)
    repositories_str = env.str("REPOSITORY", default=None)
    # Either organization or repository must be set
    if not organization and not repositories_str:
        raise ValueError(
            "ORGANIZATION and REPOSITORY environment variables were not set. Please set one"
        )

    gh_app_id = env.int("GH_APP_ID", default=None)
    gh_app_private_key_bytes = env.bytes("GH_APP_PRIVATE_KEY", default=b"")
    gh_app_installation_id = env.int("GH_APP_INSTALLATION_ID", default=None)
    gh_app_enterprise_only = env.bool("GITHUB_APP_ENTERPRISE_ONLY", default=False)

    if gh_app_id and (not gh_app_private_key_bytes or not gh_app_installation_id):
        raise ValueError(
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set"
        )

    token = env.str("GH_TOKEN", default="")
    if (
        not gh_app_id
        and not gh_app_private_key_bytes
        and not gh_app_installation_id
        and not token
    ):
        raise ValueError("GH_TOKEN environment variable not set")

    ghe = env.str("GH_ENTERPRISE_URL", default="").strip()

    start_date = validate_date_format("START_DATE")
    end_date = validate_date_format("END_DATE")

    sponsor_info = env.bool("SPONSOR_INFO", default=False)
    link_to_profile = env.bool("LINK_TO_PROFILE", default=False)

    # Separate repositories_str into a list based on the comma separator
    repositories_list = env.list("REPOSITORY", subcast=str, default=[])

    return (
        organization,
        repositories_list,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        gh_app_enterprise_only,
        token,
        ghe,
        start_date,
        end_date,
        sponsor_info,
        link_to_profile,
    )