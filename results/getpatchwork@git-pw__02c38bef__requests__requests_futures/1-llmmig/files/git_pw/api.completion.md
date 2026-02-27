### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created a `FuturesSession` instance to replace direct calls to `requests` methods (`get`, `post`, `patch`, `delete`).
3. **Asynchronous Requests**: Updated the `_get`, `_post`, `_patch`, and `_delete` functions to use the `FuturesSession` instance for making asynchronous requests. The `.result()` method is used to block and retrieve the response, ensuring compatibility with the existing synchronous code.
4. **No Other Changes**: The rest of the code remains unchanged to preserve the original functionality and structure.

### Modified Code:
```python
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
from requests_futures.sessions import FuturesSession

import git_pw
from git_pw import config

CONF = config.CONF
LOG = logging.getLogger(__name__)

Filters = ty.List[ty.Tuple[str, str]]

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()


class HTTPTokenAuth:
    """Attaches HTTP Token Authentication to the given Request object."""

    def __init__(self, token: str):
        self.token = token

    def __call__(
        self,
        r,
    ):
        r.headers['Authorization'] = self._token_auth_str(self.token)
        return r

    @staticmethod
    def _token_auth_str(token: str) -> str:
        """Return a Token auth string."""
        return 'Token {}'.format(token.strip())


def _get_auth(optional: bool = False) -> ty.Optional[HTTPTokenAuth]:
    if CONF.token:
        return HTTPTokenAuth(CONF.token)
    elif CONF.username and CONF.password:
        return (CONF.username, CONF.password)
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
    exc,
) -> None:
    if exc.response is not None and exc.response.content:
        # server errors should always be reported
        if exc.response.status_code in range(500, 512):  # 5xx Server Error
            LOG.error(
                'Server error. Please report this issue to '
                'https://github.com/getpatchwork/patchwork'
            )
            raise

        # we make the assumption that all responses will be JSON encoded
        if exc.response.status_code == 404:
            LOG.error('Resource not found')
        else:
            LOG.error(exc.response.json())
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
):
    """Make GET request and handle errors."""
    LOG.debug('GET %s', url)

    try:
        future = session.get(
            url,
            auth=_get_auth(optional=True),
            headers=_get_headers(),
            stream=stream,
            params=params,
        )
        rsp = future.result()  # Block and get the response
        rsp.raise_for_status()
    except Exception as exc:
        _handle_error('fetch', exc)

    LOG.debug('Got response')

    return rsp


def _post(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
):
    """Make POST request and handle errors."""
    LOG.debug('POST %s, data=%r', url, data)

    try:
        future = session.post(
            url, auth=_get_auth(), headers=_get_headers(), data=data
        )
        rsp = future.result()  # Block and get the response
        rsp.raise_for_status()
    except Exception as exc:
        _handle_error('create', exc)

    LOG.debug('Got response')

    return rsp


def _patch(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
):
    """Make PATCH request and handle errors."""
    LOG.debug('PATCH %s, data=%r', url, data)

    try:
        future = session.patch(
            url,
            auth=_get_auth(),
            headers=_get_headers(),
            data=data,
        )
        rsp = future.result()  # Block and get the response
        rsp.raise_for_status()
    except Exception as exc:
        _handle_error('update', exc)

    LOG.debug('Got response')

    return rsp


def _delete(url: str):
    """Make DELETE request and handle errors."""
    LOG.debug('DELETE %s', url)

    try:
        future = session.delete(url, auth=_get_auth(), headers=_get_headers())
        rsp = future.result()  # Block and get the response
        rsp.raise_for_status()
    except Exception as exc:
        _handle_error('delete', exc)

    LOG.debug('Got response')

    return rsp


# The rest of the code remains unchanged
```

### Summary:
The migration involved replacing synchronous `requests` calls with asynchronous `requests_futures` calls while ensuring the behavior remains synchronous by using `.result()` to block and retrieve the response. This approach ensures compatibility with the existing code structure.