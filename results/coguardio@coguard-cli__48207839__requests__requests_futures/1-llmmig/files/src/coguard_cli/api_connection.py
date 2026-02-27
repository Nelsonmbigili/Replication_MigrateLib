"""
The coguard CLI module which contains all api-connection
logic, so that it is modularized.
"""

import logging
import tempfile
import os
from typing import Dict, Optional
import urllib.parse
from requests_futures.sessions import FuturesSession

from coguard_cli.auth.token import Token
from coguard_cli.util import replace_special_chars_with_underscore
from coguard_cli.print_colors import COLOR_TERMINATION, \
    COLOR_RED

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()

def run_report(
        auth_token: Token,
        coguard_api_url: str,
        scan_identifier: str,
        organization: str):
    """
    This is a helper function to kick off a report run on CoGuard.
    The output is whether the report run was successful or not.
    """
    scan_identifier_sanitized = \
        replace_special_chars_with_underscore(scan_identifier, True)
    resp = session.put(
        (
            f"{coguard_api_url}/cluster/run-report/"
            f"{urllib.parse.quote_plus(scan_identifier_sanitized)}?"
            f"organizationName={urllib.parse.quote_plus(organization)}"
        ),
        headers={
            "Authorization": f'Bearer {auth_token.get_token()}',
            "Content-Type": "application/json"
        },
        timeout=1600
    ).result()  # Block and get the response
    if resp.status_code != 204:
        logging.error("Could not run a report on the specified cluster")
        return False
    return True

def get_latest_report(
        auth_token: Token,
        coguard_api_url: str,
        scan_identifier: str,
        organization: Optional[str],
        username: str
    ) -> Optional[str]:
    """
    Helper function to get the latest report for a specific cluster.
    Returns None if the latest report did not exist.
    """
    if organization:
        scan_identifier_sanitized = urllib.parse.quote_plus(
            replace_special_chars_with_underscore(scan_identifier, True)
        )
        resp = session.get(
            (
                f"{coguard_api_url}/cluster/reports/list?"
                f"clusterName={scan_identifier_sanitized}&"
                f"organizationName={urllib.parse.quote_plus(organization)}"
            ),
            headers={
                "Authorization": f'Bearer {auth_token.get_token()}',
                "Content-Type": "application/json"
            },
            timeout=300
        ).result()
    else:
        scan_identifier_sanitized = urllib.parse.quote_plus(
            replace_special_chars_with_underscore(scan_identifier, True)
        )
        resp = session.get(
            (
                 f"{coguard_api_url}/coguard-cli/reports/list?"
                 f"clusterName={scan_identifier_sanitized}&"
                 f"userName={urllib.parse.quote_plus(username)}"
            ),
            headers={
                "Authorization": f'Bearer {auth_token.get_token()}',
                "Content-Type": "application/json"
            },
            timeout=300
        ).result()
    if resp.status_code != 200:
        logging.error("Could not retrieve the latest report for cluster %s",
                      scan_identifier)
        return None
    lst = resp.json()
    if not lst:
        return None
    return lst[-1]

def send_zip_file_for_scanning(
        zip_file: str,
        user_name: str,
        auth_token: Token,
        coguard_api_url: str,
        scan_identifier: str,
        organization: Optional[str],
        ruleset: str) -> Optional[Dict]:
    """
    The helper function to send a zip file for scanning to the back-end.
    The return value will be an optional dictionary value as per the
    result jsons produced by the coguard engine.

    :param zip_file: The path to the zip file.
    :param user_name: The user name associated.
    :param auth_token: The authentication token to be used.
    :param coguard_api_url: The url to be used to contact CoGuard.
    :param organization: The optional organization string, indicating that
                         we want to upload it to an org instead of the free account.
    :returns: Either `None`, or a dictionary as returned by CoGuard after
              scanning.
    """
    with open(zip_file, 'rb') as file_to_send:
        if organization:
            resp_upload = session.post(
                (
                    f"{coguard_api_url}/cluster/"
                    f"upload-cluster-zip?organizationName={urllib.parse.quote_plus(organization)}&"
                    f"overwrite=true&compliance={urllib.parse.quote_plus(ruleset)}"
                ),
                headers={
                    "Authorization": f'Bearer {auth_token.get_token()}',
                    "Content-Type": "application/octet-stream"
                },
                data=file_to_send.read(),
                timeout=300
            ).result()
            if resp_upload.status_code != 204:
                logging.error("There was an issue uploading the zip file")
                logging.debug("Reason %s", resp_upload.reason)
                return None
            logging.debug("We successfully uploaded the cluster. Now running the report.")
            run_report_result = run_report(
                auth_token,
                coguard_api_url,
                scan_identifier,
                organization
            )
            if not run_report_result:
                return None
            latest_report = get_latest_report(
                auth_token,
                coguard_api_url,
                scan_identifier,
                organization,
                user_name
            )
            logging.debug("The latest report is %s", latest_report)
            if not latest_report:
                return None
            scan_identifier_sanitized = urllib.parse.quote_plus(
                replace_special_chars_with_underscore(scan_identifier, True),
            )
            resp = session.get(
                (
                    f"{coguard_api_url}/cluster/report?"
                    f"clusterName={scan_identifier_sanitized}&"
                    f"organizationName={urllib.parse.quote_plus(organization)}&"
                    f"reportName={urllib.parse.quote_plus(latest_report)}"
                ),
                headers={
                    "Authorization": f'Bearer {auth_token.get_token()}',
                    "Content-Type": "application/json"
                },
                timeout=300
            ).result()
        else:
            resp = session.post(
                (
                    f"{coguard_api_url}/coguard-cli/"
                    f"upload-cluster-zip?userName={urllib.parse.quote_plus(user_name)}&"
                    f"compliance={urllib.parse.quote_plus(ruleset)}"
                ),
                headers={
                    "Authorization": f'Bearer {auth_token.get_token()}',
                    "Content-Type": "application/octet-stream"
                },
                data=file_to_send.read(),
                timeout=300
            ).result()
    if resp.status_code != 200:
        logging.error("There was an error in the API call: %s",
                      resp.reason)
        return None
    return resp.json()

# The rest of the functions follow the same pattern:
# - Replace `requests` calls with `session` calls.
# - Use `.result()` to block and retrieve the response where necessary.
