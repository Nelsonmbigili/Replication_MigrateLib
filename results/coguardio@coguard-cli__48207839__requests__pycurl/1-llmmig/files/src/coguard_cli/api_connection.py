"""
The coguard CLI module which contains all api-connection
logic, so that it is modularized.
"""

import logging
import tempfile
import os
from typing import Dict, Optional
import urllib.parse
import pycurl
import json
from io import BytesIO

from coguard_cli.auth.token import Token
from coguard_cli.util import replace_special_chars_with_underscore
from coguard_cli.print_colors import COLOR_TERMINATION, \
    COLOR_RED

def _make_request(method: str, url: str, headers: Dict[str, str], data: Optional[bytes] = None, timeout: int = 300):
    """
    Helper function to make HTTP requests using pycurl.
    """
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.TIMEOUT, timeout)
    curl.setopt(pycurl.WRITEDATA, buffer)
    header_list = [f"{key}: {value}" for key, value in headers.items()]
    curl.setopt(pycurl.HTTPHEADER, header_list)

    if method == "POST":
        curl.setopt(pycurl.POST, 1)
        if data:
            curl.setopt(pycurl.POSTFIELDS, data)
    elif method == "PUT":
        curl.setopt(pycurl.CUSTOMREQUEST, "PUT")
        if data:
            curl.setopt(pycurl.POSTFIELDS, data)
    elif method == "GET":
        curl.setopt(pycurl.HTTPGET, 1)

    curl.perform()
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()
    return status_code, buffer.getvalue()

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
    url = (
        f"{coguard_api_url}/cluster/run-report/"
        f"{urllib.parse.quote_plus(scan_identifier_sanitized)}?"
        f"organizationName={urllib.parse.quote_plus(organization)}"
    )
    headers = {
        "Authorization": f'Bearer {auth_token.get_token()}',
        "Content-Type": "application/json"
    }
    status_code, _ = _make_request("PUT", url, headers, timeout=1600)
    if status_code != 204:
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
    scan_identifier_sanitized = urllib.parse.quote_plus(
        replace_special_chars_with_underscore(scan_identifier, True)
    )
    if organization:
        url = (
            f"{coguard_api_url}/cluster/reports/list?"
            f"clusterName={scan_identifier_sanitized}&"
            f"organizationName={urllib.parse.quote_plus(organization)}"
        )
    else:
        url = (
            f"{coguard_api_url}/coguard-cli/reports/list?"
            f"clusterName={scan_identifier_sanitized}&"
            f"userName={urllib.parse.quote_plus(username)}"
        )
    headers = {
        "Authorization": f'Bearer {auth_token.get_token()}',
        "Content-Type": "application/json"
    }
    status_code, response_data = _make_request("GET", url, headers, timeout=300)
    if status_code != 200:
        logging.error("Could not retrieve the latest report for cluster %s",
                      scan_identifier)
        return None
    lst = json.loads(response_data.decode('utf-8'))
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
        file_data = file_to_send.read()
        if organization:
            url = (
                f"{coguard_api_url}/cluster/"
                f"upload-cluster-zip?organizationName={urllib.parse.quote_plus(organization)}&"
                f"overwrite=true&compliance={urllib.parse.quote_plus(ruleset)}"
            )
        else:
            url = (
                f"{coguard_api_url}/coguard-cli/"
                f"upload-cluster-zip?userName={urllib.parse.quote_plus(user_name)}&"
                f"compliance={urllib.parse.quote_plus(ruleset)}"
            )
        headers = {
            "Authorization": f'Bearer {auth_token.get_token()}',
            "Content-Type": "application/octet-stream"
        }
        status_code, response_data = _make_request("POST", url, headers, data=file_data, timeout=300)
        if status_code != 204:
            logging.error("There was an issue uploading the zip file")
            return None
        return json.loads(response_data.decode('utf-8'))
