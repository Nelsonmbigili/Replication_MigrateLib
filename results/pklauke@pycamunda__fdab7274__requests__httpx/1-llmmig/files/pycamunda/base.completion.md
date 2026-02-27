### Explanation of Changes
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Import Replacement**: Replaced `requests` with `httpx` in the import statements.
2. **Session Handling**: Replaced `requests.Session` with `httpx.Client` for session-based requests.
3. **Request Method**: Replaced `requests.request` with `httpx.request` for making HTTP requests.
4. **Exception Handling**: Updated exception handling to use `httpx.RequestError` instead of `requests.exceptions.RequestException`.
5. **Response Object**: Updated the type hints and references to the response object to use `httpx.Response` instead of `requests.Response`.
6. **File Uploads**: The `files` parameter in `httpx` works similarly to `requests`, so no changes were needed for file handling.
7. **Raise for Status**: Updated the `_raise_for_status` function to accept `httpx.Response` instead of `requests.Response`.

### Modified Code
```python
# -*- coding: utf-8 -*-

import enum
import datetime as dt
import typing
import json

import httpx

import pycamunda.request


__all__ = ['isoformat', 'from_isoformat']


def value_is_true(self, obj: typing.Any, obj_type: typing.Any) -> bool:
    return bool(obj.__dict__[self.name])


class RequestMethod(enum.Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'


class CamundaRequest(pycamunda.request.Request):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth = None
        self.session = None
        self._files = None

    @property
    def files(self):
        return self._files

    def __call__(self, method: RequestMethod, *args, **kwargs) -> httpx.Response:
        try:
            if self.session is not None:
                kwargs = {}
                if self.auth is not None:
                    kwargs['auth'] = self.auth
                response = self.session.request(
                    method=method.value,
                    url=self.url,
                    params=self.query_parameters(),
                    json=self.body_parameters(),
                    files=self.files,
                    **kwargs
                )
            else:
                response = httpx.request(
                    method=method.value,
                    url=self.url,
                    params=self.query_parameters(),
                    json=self.body_parameters(),
                    auth=self.auth,
                    files=self.files
                )
        except httpx.RequestError as exc:
            raise pycamunda.PyCamundaException(exc)
        if not response:
            pycamunda.base._raise_for_status(response)

        return response

    def body_parameters(self, apply: typing.Callable = ...):
        if apply is Ellipsis:
            return super().body_parameters(apply=prepare)
        return super().body_parameters(apply=apply)

    def query_parameters(self, apply: typing.Callable = ...):
        if apply is Ellipsis:
            return super().query_parameters(apply=query_prepare)
        return super().query_parameters(apply=apply)


def isoformat(datetime_: typing.Union[dt.date, dt.datetime]) -> str:
    """Convert a datetime object to the isoformat string Camunda expects. Datetime objects are
    expected to contain timezoneinformation.

    :param datetime_: Datetime or date object to convert.
    :return: Isoformat datetime or date string.
    """
    if isinstance(datetime_, dt.datetime):
        dt_str = datetime_.strftime('%Y-%m-%dT%H:%M:%S.{ms}%z')
        ms = datetime_.microsecond // 1000
        dt_str = dt_str.format(ms=str(ms).zfill(3))
    else:
        dt_str = datetime_.strftime('%Y-%m-%d')

    return dt_str


def from_isoformat(datetime_str: str) -> dt.datetime:
    """Convert an isoformat string to a datetime object.

    :param datetime_str: String to convert.
    :return: Converted datetime.
    """
    return dt.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')


def prepare(value: typing.Any) -> typing.Any:
    """Prepare parameter values for Camunda.

    :param value: Value to prepare.
    """
    if isinstance(value, dt.datetime):
        return isoformat(datetime_=value)
    try:  # support for enums
        value = value.value
    except AttributeError:
        pass
    return value


def query_prepare(value: typing.Any) -> typing.Any:
    """Prepare parameter values for Camunda including converting boolean values to lowercase
    strings.

    :param value: Value to prepare.
    """
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return prepare(value)


def _raise_for_status(response: httpx.Response) -> None:
    """Handle http errors regarding Camunda.

    :param response: Response coming from Camunda.
    """
    try:
        message = response.json()['message']
    except KeyError:
        message = ''
    except TypeError:
        message = ''
    except json.decoder.JSONDecodeError:
        message = ''

    if response.status_code == 400:
        raise pycamunda.BadRequest(message)
    if response.status_code == 401:
        raise pycamunda.Unauthorized(message)
    elif response.status_code == 403:
        raise pycamunda.Forbidden(message)
    elif response.status_code == 404:
        raise pycamunda.NotFound(message)

    raise pycamunda.NoSuccess(response.text)


class _PathMixin:
    @property
    def url(self):
        if self.id_ is not None:
            return self._url.format(path=self.id_)
        if self.tenant_id is not None:
            return self._url.format(path=f'key/{self.key}/tenant-id/{self.tenant_id}')
        return self._url.format(path=f'key/{self.key}')
```

### Summary of Changes
- Replaced `requests` with `httpx` in all relevant parts of the code.
- Updated exception handling and response handling to align with `httpx`'s API.
- Ensured compatibility with `httpx`'s session and request methods.