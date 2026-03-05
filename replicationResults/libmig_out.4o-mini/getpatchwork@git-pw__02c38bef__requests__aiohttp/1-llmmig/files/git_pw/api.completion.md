### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Asynchronous Functions**: The `aiohttp` library is designed for asynchronous programming, so all functions that make HTTP requests were modified to be asynchronous (`async def`), and the `await` keyword was used when calling the HTTP methods.

2. **Session Management**: Instead of calling `requests.get`, `requests.post`, etc., we now create an `aiohttp.ClientSession` and use its methods (`session.get`, `session.post`, etc.) to make requests.

3. **Response Handling**: The response handling was updated to use `await response.json()` instead of `response.json()` since the response methods in `aiohttp` are asynchronous.

4. **Error Handling**: The error handling was adjusted to work with `aiohttp` exceptions instead of `requests.exceptions.RequestException`.

5. **Stream Handling**: The streaming of responses was adapted to use `async for` to read the response content in chunks.

6. **Function Signatures**: The functions that make HTTP requests now return `async` results, which may require changes in how they are called in the rest of the application.

Here is the modified code:

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
import aiohttp

import git_pw
from git_pw import config

CONF = config.CONF
LOG = logging.getLogger(__name__)

Filters = ty.List[ty.Tuple[str, str]]


class HTTPTokenAuth:
    """Attaches HTTP Token Authentication to the given Request object."""

    def __init__(self, token: str):
        self.token = token

    def __call__(self, headers: ty.Dict[str, str]) -> ty.Dict[str, str]:
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
        return aiohttp.BasicAuth(CONF.username, CONF.password)
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


def _get_project() -> str:
    if CONF.project and CONF.project.strip() == '*':
        return ''  # just don't bother filtering on project
    elif CONF.project:
        return CONF.project.strip()
    else:
        LOG.error('Project information missing')
        LOG.error(
            'You must provide project information via git-config or '
            'via --project'
        )
        LOG.error('To list all projects, set project to "*"')
        sys.exit(1)


def _handle_error(
    operation: str,
    exc: aiohttp.ClientError,
) -> None:
    if hasattr(exc, 'response') and exc.response is not None:
        # server errors should always be reported
        if exc.response.status in range(500, 512):  # 5xx Server Error
            LOG.error(
                'Server error. Please report this issue to '
                'https://github.com/getpatchwork/patchwork'
            )
            raise

        # we make the assumption that all responses will be JSON encoded
        if exc.response.status == 404:
            LOG.error('Resource not found')
        else:
            LOG.error(await exc.response.json())
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


async def _get(
    url: str,
    params: ty.Optional[Filters] = None,
    stream: bool = False,
) -> aiohttp.ClientResponse:
    """Make GET request and handle errors."""
    LOG.debug('GET %s', url)

    async with aiohttp.ClientSession() as session:
        try:
            rsp = await session.get(
                url,
                auth=_get_auth(optional=True),
                headers=_get_headers(),
                params=params,
            )
            rsp.raise_for_status()
        except aiohttp.ClientError as exc:
            _handle_error('fetch', exc)

    LOG.debug('Got response')

    return rsp


async def _post(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> aiohttp.ClientResponse:
    """Make POST request and handle errors."""
    LOG.debug('POST %s, data=%r', url, data)

    async with aiohttp.ClientSession() as session:
        try:
            rsp = await session.post(
                url, auth=_get_auth(), headers=_get_headers(), data=data
            )
            rsp.raise_for_status()
        except aiohttp.ClientError as exc:
            _handle_error('create', exc)

    LOG.debug('Got response')

    return rsp


async def _patch(
    url: str,
    data: ty.List[ty.Tuple[str, ty.Any]],
) -> aiohttp.ClientResponse:
    """Make PATCH request and handle errors."""
    LOG.debug('PATCH %s, data=%r', url, data)

    async with aiohttp.ClientSession() as session:
        try:
            rsp = await session.patch(
                url,
                auth=_get_auth(),
                headers=_get_headers(),
                data=data,
            )
            rsp.raise_for_status()
        except aiohttp.ClientError as exc:
            _handle_error('update', exc)

    LOG.debug('Got response')

    return rsp


async def _delete(url: str) -> aiohttp.ClientResponse:
    """Make DELETE request and handle errors."""
    LOG.debug('DELETE %s', url)

    async with aiohttp.ClientSession() as session:
        try:
            rsp = await session.delete(url, auth=_get_auth(), headers=_get_headers())
            rsp.raise_for_status()
        except aiohttp.ClientError as exc:
            _handle_error('delete', exc)

    LOG.debug('Got response')

    return rsp


async def version() -> ty.Tuple[int, int]:
    """Get the version of the server from the URL, if present."""
    server = _get_server()

    version = re.match(r'.*/(\d)\.(\d)$', server)
    if version:
        return (int(version.group(1)), int(version.group(2)))

    # return the oldest version we support if no version provided
    return (1, 0)


async def download(
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
    rsp = await _get(url, params, stream=True)

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
        # we use iter_content because patches can be binary
        async for block in rsp.content.iter_any(1024):
            output_file.write(block)
    finally:
        output_file.close()

    return output_path


async def index(resource_type: str, params: ty.Optional[Filters] = None) -> dict:
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

    return await (await _get(url, params)).json()


async def detail(
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

    return await (await _get(url, params, stream=False)).json()


async def create(
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

    return await (await _post(url, data)).json()


async def delete(resource_type: str, resource_id: ty.Union[str, int]) -> None:
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

    await _delete(url)


async def update(
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

    return await (await _patch(url, data)).json()


def validate_minimum_version(
    min_version: ty.Tuple[int, int],
    msg: str,
) -> ty.Callable[[ty.Any], ty.Any]:
    def inner(f):
        @click.pass_context
        async def new_func(ctx, *args, **kwargs):
            if await version() < min_version:
                LOG.error(msg)
                sys.exit(1)

            return await ctx.invoke(f, *args, **kwargs)

        return update_wrapper(new_func, f)

    return inner


def validate_multiple_filter_support(f: ty.Callable) -> ty.Callable:
    @click.pass_context
    async def new_func(ctx, *args, **kwargs):
        if await version() >= (1, 1):
            return await ctx.invoke(f, *args, **kwargs)

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

        return await ctx.invoke(f, *args, **kwargs)

    return update_wrapper(new_func, f)


async def retrieve_filter_ids(
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
        # protect against really generic (and essentially meaningless) queries
        LOG.error('Filters must be at least 3 characters long')
        sys.exit(1)

    # NOTE(stephenfin): This purposefully ignores the possibility of a second
    # page because it's unlikely and likely unnecessary
    items = await index(resource_type, [('q', filter_value)])
    if len(items) == 0:
        LOG.warning('No matching %s found: %s', filter_name, filter_value)
    elif len(items) > 1 and await version() < (1, 1):
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
```

This code now uses `aiohttp` for asynchronous HTTP requests, allowing for non-blocking operations which can improve performance in applications that require multiple concurrent requests.