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

def _handle_error(
    operation: str,
    exc: requests.exceptions.RequestException,
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