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
import treq
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred

import git_pw
from git_pw import config

CONF = config.CONF
LOG = logging.getLogger(__name__)

Filters = ty.List[ty.Tuple[str, str]]


class HTTPTokenAuth:
    """Attaches HTTP Token Authentication to the given Request object."""

    def __init__(self, token: str):
        self.token = token

    def add_auth(self, headers: ty.Dict[str, str]) -> None:
        headers['Authorization'] = self._token_auth_str(self.token)

    @staticmethod
    def _token_auth_str(token: str) -> str:
        """Return a Token auth string."""
        return 'Token {}'.format(token.strip())


def _get_auth(optional: bool = False) -> ty.Optional[HTTPTokenAuth]:
    if CONF.token:
        return HTTPTokenAuth(CONF.token)
    elif CONF.username and CONF.password:
        LOG.error('Basic authentication is not supported with treq')
        sys.exit(1)
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


@inlineCallbacks
def _handle_error(operation: str, response) -> Deferred:
    if response is not None:
        content = yield response.text()
        if response.code in range(500, 512):  # 5xx Server Error
            LOG.error(
                'Server error. Please report this issue to '
                'https://github.com/getpatchwork/patchwork'
            )
            raise Exception(content)

        if response.code == 404:
            LOG.error('Resource not found')
        else:
            LOG.error(content)
    else:
        LOG.error(
            'Failed to %s resource. Is your configuration '
            'correct?' % operation
        )
        LOG.error("Use the '--debug' flag for more information")

    if CONF.debug:
        raise Exception('Debug mode enabled, raising exception')
    else:
        sys.exit(1)


@inlineCallbacks
def _get(
    url: str,
    params: ty.Optional[Filters] = None,
    stream: bool = False,
) -> Deferred:
    """Make GET request and handle errors."""
    LOG.debug('GET %s', url)

    headers = _get_headers()
    auth = _get_auth(optional=True)
    if auth:
        auth.add_auth(headers)

    try:
        rsp = yield treq.get(url, headers=headers, params=params, allow_redirects=True)
        if rsp.code >= 400:
            yield _handle_error('fetch', rsp)
    except Exception as exc:
        LOG.error('Exception during GET request: %s', exc)
        raise

    LOG.debug('Got response')
    returnValue(rsp)


@inlineCallbacks
def _post(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> Deferred:
    """Make POST request and handle errors."""
    LOG.debug('POST %s, data=%r', url, data)

    headers = _get_headers()
    auth = _get_auth()
    if auth:
        auth.add_auth(headers)

    try:
        rsp = yield treq.post(url, headers=headers, data=data)
        if rsp.code >= 400:
            yield _handle_error('create', rsp)
    except Exception as exc:
        LOG.error('Exception during POST request: %s', exc)
        raise

    LOG.debug('Got response')
    returnValue(rsp)


@inlineCallbacks
def _patch(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> Deferred:
    """Make PATCH request and handle errors."""
    LOG.debug('PATCH %s, data=%r', url, data)

    headers = _get_headers()
    auth = _get_auth()
    if auth:
        auth.add_auth(headers)

    try:
        rsp = yield treq.patch(url, headers=headers, data=data)
        if rsp.code >= 400:
            yield _handle_error('update', rsp)
    except Exception as exc:
        LOG.error('Exception during PATCH request: %s', exc)
        raise

    LOG.debug('Got response')
    returnValue(rsp)


@inlineCallbacks
def _delete(url: str) -> Deferred:
    """Make DELETE request and handle errors."""
    LOG.debug('DELETE %s', url)

    headers = _get_headers()
    auth = _get_auth()
    if auth:
        auth.add_auth(headers)

    try:
        rsp = yield treq.delete(url, headers=headers)
        if rsp.code >= 400:
            yield _handle_error('delete', rsp)
    except Exception as exc:
        LOG.error('Exception during DELETE request: %s', exc)
        raise

    LOG.debug('Got response')
    returnValue(rsp)


@inlineCallbacks
def download(
    url: str,
    params: ty.Optional[Filters] = None,
    output: ty.Optional[ty.Optional[str]] = None,
) -> Deferred:
    """Retrieve a specific API resource and save it to a file/stdout."""
    rsp = yield _get(url, params, stream=True)

    header = re.search(
        'filename=(.+)',
        rsp.headers.get('content-disposition') or '',
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
        # Use treq's iter_chunks for streaming
        async for block in rsp.iter_chunks(1024):
            output_file.write(block)
    finally:
        output_file.close()

    returnValue(output_path)
