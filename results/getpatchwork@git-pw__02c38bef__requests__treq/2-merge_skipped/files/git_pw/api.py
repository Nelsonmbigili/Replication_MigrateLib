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
    return output_path


def index(resource_type: str, params: ty.Optional[Filters] = None) -> dict:
    """List API resources.

    GET /{resource}/

    All resources are JSON bodies, thus we can access them in a similar
    fashion.

    Arguments:
        resource_type: The resource endpoint name.
        params: Additional parameters, filters.

    Returns:
        A list of dictionaries, representing the summary view of each resource.
    """
    # NOTE(stephenfin): All resources must have a trailing '/'
    url = '/'.join([_get_server(), resource_type, ''])

    # NOTE(stephenfin): Not all endpoints in the Patchwork API allow filtering
    # by project, but all the ones we care about here do.
    params = params or []
    params.append(('project', _get_project()))

    return _get(url, params).json()


def detail(
    resource_type: str,
    resource_id: ty.Union[str, int],
    params: ty.Optional[Filters] = None,
) -> ty.Dict:
    """Retrieve a specific API resource.

    GET /{resource}/{resourceID}/

    Arguments:
        resource_type: The resource endpoint name.
        resource_id: The ID for the specific resource.
        params: Additional parameters.

    Returns:
        A dictionary representing the detailed view of a given resource.
    """
    # NOTE(stephenfin): All resources must have a trailing '/'
    url = '/'.join([_get_server(), resource_type, str(resource_id), ''])

    return _get(url, params, stream=False).json()


def create(
    resource_type: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> dict:
    """Create a new API resource.

    POST /{resource}/

    Arguments:
        resource_type: The resource endpoint name.
        params: Fields to update.

    Returns:
        A dictionary representing the detailed view of a given resource.
    """
    # NOTE(stephenfin): All resources must have a trailing '/'
    url = '/'.join([_get_server(), resource_type, ''])

    return _post(url, data).json()


def delete(resource_type: str, resource_id: ty.Union[str, int]) -> None:
    """Delete a specific API resource.

    DELETE /{resource}/{resourceID}/

    Arguments:
        resource_type: The resource endpoint name.
        resource_id: The ID for the specific resource.

    Returns:
        A dictionary representing the detailed view of a given resource.
    """
    # NOTE(stephenfin): All resources must have a trailing '/'
    url = '/'.join([_get_server(), resource_type, str(resource_id), ''])

    _delete(url)


def update(
    resource_type: str,
    resource_id: ty.Union[str, int],
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> dict:
    """Update a specific API resource.

    PATCH /{resource}/{resourceID}/

    Arguments:
        resource_type: The resource endpoint name.
        resource_id: The ID for the specific resource.
        params: Fields to update.

    Returns:
        A dictionary representing the detailed view of a given resource.
    """
    # NOTE(stephenfin): All resources must have a trailing '/'
    url = '/'.join([_get_server(), resource_type, str(resource_id), ''])

    return _patch(url, data).json()


def validate_minimum_version(
    min_version: ty.Tuple[int, int],
    msg: str,
) -> ty.Callable[[ty.Any], ty.Any]:
    def inner(f):
        @click.pass_context
        def new_func(ctx, *args, **kwargs):
            if version() < min_version:
                LOG.error(msg)
                sys.exit(1)

            return ctx.invoke(f, *args, **kwargs)

        return update_wrapper(new_func, f)

    return inner


def validate_multiple_filter_support(f: ty.Callable) -> ty.Callable:
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        if version() >= (1, 1):
            return ctx.invoke(f, *args, **kwargs)

        for param in ctx.command.params:
            if not param.multiple:
                continue

            if param.name in ('headers'):
                continue

            value = list(kwargs[param.name] or [])
            if value and len(value) > 1 and value != param.default:
                msg = (
                    'The `--%s` filter was specified multiple times. '
                    'Filtering by multiple %ss is not supported with API '
                    'version 1.0. If the server supports it, use version '
                    '1.1 instead. Refer to https://tinyurl.com/2p8swbpn for '
                    'more information.'
                )

                LOG.warning(msg, param.name, param.name)

        return ctx.invoke(f, *args, **kwargs)

    return update_wrapper(new_func, f)


def retrieve_filter_ids(
    resource_type: str,
    filter_name: str,
    filter_value: str,
) -> ty.List[ty.Tuple[str, str]]:
    """Retrieve IDs for items passed through by filter.

    Some filters require client-side filtering, e.g. filtering patches by
    submitter names.

    Arguments:
        resource_type: The filter's resource endpoint name.
        filter_name: The name of the filter.
        filter_value: The value of the filter.

    Returns:
        A list of querystring key-value pairs to use in the actual request.
    """
    if len(filter_value) < 3:
        # protect agaisnt really generic (and essentially meaningless) queries
        LOG.error('Filters must be at least 3 characters long')
        sys.exit(1)

    # NOTE(stephenfin): This purposefully ignores the possiblity of a second
    # page because it's unlikely and likely unnecessary
    items = index(resource_type, [('q', filter_value)])
    if len(items) == 0:
        LOG.warning('No matching %s found: %s', filter_name, filter_value)
    elif len(items) > 1 and version() < (1, 1):
        # we don't support multiple filters in 1.0
        msg = (
            'More than one match for found for `--%s=%s`. '
            'Filtering by multiple %ss is not supported with '
            'API version 1.0. If the server supports it, use '
            'version 1.1 instead. Refer to https://tinyurl.com/2p8swbpn '
            'for more information.'
        )

        LOG.warning(msg, filter_name, filter_value, filter_name)

    return [(filter_name, item['id']) for item in items]