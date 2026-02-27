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
import httpx

import git_pw
from git_pw import config

CONF = config.CONF
LOG = logging.getLogger(__name__)

Filters = ty.List[ty.Tuple[str, str]]


class HTTPTokenAuth(httpx.Auth):
    """Attaches HTTP Token Authentication to the given Request object."""

    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request: httpx.Request) -> ty.Generator[httpx.Request, httpx.Response, None]:
        request.headers['Authorization'] = self._token_auth_str(self.token)
        yield request

    @staticmethod
    def _token_auth_str(token: str) -> str:
        """Return a Token auth string."""
        return 'Token {}'.format(token.strip())


def _get_auth(optional: bool = False) -> ty.Optional[httpx.Auth]:
    if CONF.token:
        return HTTPTokenAuth(CONF.token)
    elif CONF.username and CONF.password:
        return httpx.BasicAuth(CONF.username, CONF.password)
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
            # NOTE(stephenfin): We've already handled this particular error
            # above so we don't warn twice. We also don't stick on a version
            # number since the user clearly wants the latest
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
    exc: httpx.RequestError,
) -> None:
    if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
        if exc.response.status_code in range(500, 512):  # 5xx Server Error
            LOG.error(
                'Server error. Please report this issue to '
                'https://github.com/getpatchwork/patchwork'
            )
            raise

        if exc.response.status_code == 404:
            LOG.error('Resource not found')
        else:
            try:
                LOG.error(exc.response.json())
            except ValueError:
                LOG.error('Failed to parse error response as JSON')
    else:
        LOG.error(
            'Failed to %s resource. Is your configuration '
            'correct?' % operation
        )
        LOG.error("Use the '--debug' flag for more information")

    if CONF.debug:
        raise
    else:
        sys.exit(1)


def _get(
    url: str,
    params: ty.Optional[Filters] = None,
    stream: bool = False,
) -> httpx.Response:
    """Make GET request and handle errors."""
    LOG.debug('GET %s', url)

    try:
        with httpx.Client() as client:
            rsp = client.get(
                url,
                auth=_get_auth(optional=True),
                headers=_get_headers(),
                params=params,
                stream=stream,
            )
            rsp.raise_for_status()
    except httpx.RequestError as exc:
        _handle_error('fetch', exc)

    LOG.debug('Got response')

    return rsp


def _post(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> httpx.Response:
    """Make POST request and handle errors."""
    LOG.debug('POST %s, data=%r', url, data)

    try:
        with httpx.Client() as client:
            rsp = client.post(
                url, auth=_get_auth(), headers=_get_headers(), data=data
            )
            rsp.raise_for_status()
    except httpx.RequestError as exc:
        _handle_error('create', exc)

    LOG.debug('Got response')

    return rsp


def _patch(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> httpx.Response:
    """Make PATCH request and handle errors."""
    LOG.debug('PATCH %s, data=%r', url, data)

    try:
        with httpx.Client() as client:
            rsp = client.patch(
                url,
                auth=_get_auth(),
                headers=_get_headers(),
                data=data,
            )
            rsp.raise_for_status()
    except httpx.RequestError as exc:
        _handle_error('update', exc)

    LOG.debug('Got response')

    return rsp


def _delete(url: str) -> httpx.Response:
    """Make DELETE request and handle errors."""
    LOG.debug('DELETE %s', url)

    try:
        with httpx.Client() as client:
            rsp = client.delete(url, auth=_get_auth(), headers=_get_headers())
            rsp.raise_for_status()
    except httpx.RequestError as exc:
        _handle_error('delete', exc)

    LOG.debug('Got response')

    return rsp


def download(
    url: str,
    params: ty.Optional[Filters] = None,
    output: ty.Optional[ty.Optional[str]] = None,
) -> ty.Optional[str]:
    """Retrieve a specific API resource and save it to a file/stdout.

    The ``Content-Disposition`` header is assumed to be present and
    will be used for the output filename, if not writing to stdout.

    Arguments:
        url: The resource URL.
        params: Additional parameters.
        output: The output file. If output is a directory then
            the file name will be according to the patch subject and
            will be downloaded into the output directory.
            If None, a temporary file will be used.

    Returns:
        A path to an output file containing the content, else None if stdout
        used.
    """
    rsp = _get(url, params, stream=True)

    # we don't catch anything here because we should break if these are missing
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
        # we use iter_bytes because patches can be binary
        for block in rsp.iter_bytes(1024):
            output_file.write(block)
    finally:
        output_file.close()

    return output_path
