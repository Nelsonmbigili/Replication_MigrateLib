"""
Simple wrappers around request methods.
"""

from functools import update_wrapper
import logging
import os.path
import re
import sys
import tempfile
import typing as ty

import click
import urllib3
from urllib3.exceptions import HTTPError

import git_pw
from git_pw import config

CONF = config.CONF
LOG = logging.getLogger(__name__)

Filters = ty.List[ty.Tuple[str, str]]

# Initialize a global PoolManager for connection reuse
HTTP = urllib3.PoolManager()


class HTTPTokenAuth:
    """Attaches HTTP Token Authentication to the given Request object."""

    def __init__(self, token: str):
        self.token = token

    def add_auth(self, headers: ty.Dict[str, str]) -> ty.Dict[str, str]:
        headers['Authorization'] = self._token_auth_str(self.token)
        return headers

    @staticmethod
    def _token_auth_str(token: str) -> str:
        """Return a Token auth string."""
        return 'Token {}'.format(token.strip())


def _get_auth(optional: bool = False) -> ty.Optional[HTTPTokenAuth]:
    if CONF.token:
        return HTTPTokenAuth(CONF.token)
    elif CONF.username and CONF.password:
        # Basic Auth is handled by adding the Authorization header manually
        auth_str = f"{CONF.username}:{CONF.password}"
        encoded_auth = urllib3.util.make_headers(basic_auth=auth_str)
        return lambda headers: {**headers, **encoded_auth}
    elif not optional:
        LOG.error('Authentication information missing')
        LOG.error(
            'You must configure authentication via git-config or via '
            '--token or --username, --password'
        )
        sys.exit(1)
    return None


def _get_headers() -> ty.Dict[str, str]:
    return {
        'User-Agent': 'git-pw ({})'.format(git_pw.__version__),
    }


def _get_server() -> str:
    if CONF.server:
        server = CONF.server.rstrip('/')

        if not re.match(r'.*/api/\d\.\d$', server):
            LOG.warning('Server version missing')
            LOG.warning(
                'You should provide the server version in the URL '
                'configured via git-config or --server'
            )
            LOG.warning('This will be required in git-pw 2.0')

        if not re.match(r'.*/api(/\d\.\d)?$', server):
            server += '/api'

        return server
    else:
        LOG.error('Server information missing')
        LOG.error(
            'You must provide server information via git-config or via '
            '--server'
        )
        sys.exit(1)


def _handle_error(
    operation: str,
    exc: HTTPError,
    status_code: int = None,
    response_data: ty.Optional[bytes] = None,
) -> None:
    if status_code and 500 <= status_code < 512:
        LOG.error(
            'Server error. Please report this issue to '
            'https://github.com/getpatchwork/patchwork'
        )
        raise

    if status_code == 404:
        LOG.error('Resource not found')
    elif response_data:
        LOG.error(response_data.decode('utf-8'))
    else:
        LOG.error(
            'Failed to %s resource. Is your configuration '
            'correct?' % operation
        )
        LOG.error("Use the '--debug' flag for more information")

    if CONF.debug:
        raise exc
    else:
        sys.exit(1)


def _request(
    method: str,
    url: str,
    params: ty.Optional[Filters] = None,
    headers: ty.Optional[ty.Dict[str, str]] = None,
    body: ty.Optional[ty.Any] = None,
    stream: bool = False,
) -> urllib3.response.HTTPResponse:
    """Make an HTTP request and handle errors."""
    headers = headers or {}
    if params:
        url += '?' + urllib3.request.urlencode(params)

    try:
        response = HTTP.request(
            method,
            url,
            headers=headers,
            body=body,
            preload_content=not stream,
        )
        if response.status >= 400:
            raise HTTPError(f"HTTP {response.status}", response=response)
    except HTTPError as exc:
        _handle_error(method, exc, response.status, response.data if response else None)

    return response


def _get(
    url: str,
    params: ty.Optional[Filters] = None,
    stream: bool = False,
) -> urllib3.response.HTTPResponse:
    """Make GET request and handle errors."""
    LOG.debug('GET %s', url)
    headers = _get_headers()
    auth = _get_auth(optional=True)
    if auth:
        headers = auth.add_auth(headers)

    return _request('GET', url, params=params, headers=headers, stream=stream)


def _post(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> urllib3.response.HTTPResponse:
    """Make POST request and handle errors."""
    LOG.debug('POST %s, data=%r', url, data)
    headers = _get_headers()
    auth = _get_auth()
    if auth:
        headers = auth.add_auth(headers)

    encoded_data = urllib3.request.urlencode(data)
    return _request('POST', url, headers=headers, body=encoded_data)


def _patch(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> urllib3.response.HTTPResponse:
    """Make PATCH request and handle errors."""
    LOG.debug('PATCH %s, data=%r', url, data)
    headers = _get_headers()
    auth = _get_auth()
    if auth:
        headers = auth.add_auth(headers)

    encoded_data = urllib3.request.urlencode(data)
    return _request('PATCH', url, headers=headers, body=encoded_data)


def _delete(url: str) -> urllib3.response.HTTPResponse:
    """Make DELETE request and handle errors."""
    LOG.debug('DELETE %s', url)
    headers = _get_headers()
    auth = _get_auth()
    if auth:
        headers = auth.add_auth(headers)

    return _request('DELETE', url, headers=headers)


# The rest of the code remains unchanged, except for replacing `requests.Response` with `urllib3.response.HTTPResponse` where necessary.
