"""
Simple wrappers around HTTP methods using pycurl.
"""

from functools import update_wrapper
import logging
import os.path
import re
import sys
import tempfile
import typing as ty
from io import BytesIO

import click
import pycurl

import git_pw
from git_pw import config

CONF = config.CONF
LOG = logging.getLogger(__name__)

Filters = ty.List[ty.Tuple[str, str]]


class HTTPTokenAuth:
    """Handles HTTP Token Authentication."""

    def __init__(self, token: str):
        self.token = token

    def apply(self, curl: pycurl.Curl) -> None:
        """Apply token authentication to the curl object."""
        curl.setopt(pycurl.HTTPHEADER, [f"Authorization: Token {self.token.strip()}"])


class HTTPBasicAuth:
    """Handles HTTP Basic Authentication."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def apply(self, curl: pycurl.Curl) -> None:
        """Apply basic authentication to the curl object."""
        curl.setopt(pycurl.USERPWD, f"{self.username}:{self.password}")


def _get_auth(optional: bool = False) -> ty.Optional[ty.Callable[[pycurl.Curl], None]]:
    if CONF.token:
        return HTTPTokenAuth(CONF.token)
    elif CONF.username and CONF.password:
        return HTTPBasicAuth(CONF.username, CONF.password)
    elif not optional:
        LOG.error('Authentication information missing')
        LOG.error(
            'You must configure authentication via git-config or via '
            '--token or --username, --password'
        )
        sys.exit(1)
    return None


def _get_headers() -> ty.List[str]:
    return [
        f"User-Agent: git-pw ({git_pw.__version__})",
    ]


def _perform_request(curl: pycurl.Curl, url: str, method: str, **kwargs) -> BytesIO:
    """Perform an HTTP request using pycurl."""
    buffer = BytesIO()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    curl.setopt(pycurl.CUSTOMREQUEST, method)

    # Apply headers
    headers = _get_headers()
    if "headers" in kwargs:
        headers.extend(kwargs["headers"])
    curl.setopt(pycurl.HTTPHEADER, headers)

    # Apply authentication
    auth = _get_auth(optional=kwargs.get("optional_auth", False))
    if auth:
        auth.apply(curl)

    # Apply data for POST/PATCH
    if "data" in kwargs and kwargs["data"]:
        curl.setopt(pycurl.POSTFIELDS, kwargs["data"])

    # Perform the request
    try:
        curl.perform()
    except pycurl.error as e:
        LOG.error(f"Failed to {method} resource: {e}")
        sys.exit(1)

    # Check for HTTP errors
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    if status_code >= 400:
        LOG.error(f"HTTP error {status_code} for {method} {url}")
        sys.exit(1)

    return buffer


def _get(url: str, params: ty.Optional[Filters] = None, stream: bool = False) -> BytesIO:
    """Make GET request and handle errors."""
    LOG.debug('GET %s', url)

    if params:
        query_string = "&".join(f"{k}={v}" for k, v in params)
        url = f"{url}?{query_string}"

    curl = pycurl.Curl()
    response = _perform_request(curl, url, "GET", optional_auth=True)
    curl.close()

    return response


def _post(url: str, data: ty.List[ty.Tuple[str, ty.Any]]) -> BytesIO:
    """Make POST request and handle errors."""
    LOG.debug('POST %s, data=%r', url, data)

    curl = pycurl.Curl()
    response = _perform_request(curl, url, "POST", data="&".join(f"{k}={v}" for k, v in data))
    curl.close()

    return response


def _patch(url: str, data: ty.List[ty.Tuple[str, ty.Any]]) -> BytesIO:
    """Make PATCH request and handle errors."""
    LOG.debug('PATCH %s, data=%r', url, data)

    curl = pycurl.Curl()
    response = _perform_request(curl, url, "PATCH", data="&".join(f"{k}={v}" for k, v in data))
    curl.close()

    return response


def _delete(url: str) -> None:
    """Make DELETE request and handle errors."""
    LOG.debug('DELETE %s', url)

    curl = pycurl.Curl()
    _perform_request(curl, url, "DELETE")
    curl.close()


def download(
    url: str,
    params: ty.Optional[Filters] = None,
    output: ty.Optional[ty.Optional[str]] = None,
) -> ty.Optional[str]:
    """Retrieve a specific API resource and save it to a file/stdout."""
    rsp = _get(url, params, stream=True)

    # Extract filename from headers
    header = re.search(
        'filename=(.+)',
        rsp.getvalue().decode('utf-8'),
    )
    if not header:
        LOG.error('Filename was expected but was not provided in response')
        sys.exit(1)

    if output == '-':
        output_path = output
        output_file = sys.stdout.buffer
    else:
        if output:
            output_path = output
            if os.path.isdir(output):
                output_path = os.path.join(output, header.group(1))
        else:
            output_path = os.path.join(
                tempfile.mkdtemp(prefix='git-pw'),
                header.group(1),
            )
        LOG.debug('Saving to %s', output_path)
        output_file = open(output_path, 'wb')

    try:
        output_file.write(rsp.getvalue())
    finally:
        output_file.close()

    return output_path
