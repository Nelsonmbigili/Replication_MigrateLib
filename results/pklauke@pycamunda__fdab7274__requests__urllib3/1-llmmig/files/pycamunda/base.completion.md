### Explanation of Changes

To migrate the code from the `requests` library to the `urllib3` library, the following changes were made:

1. **Replaced `requests` imports**: Removed the `requests` import and replaced it with `urllib3`.
2. **Session Handling**: Replaced `requests.Session` with `urllib3.PoolManager` for managing HTTP connections.
3. **HTTP Requests**: Replaced `requests.request` and `session.request` with `urllib3.PoolManager.request`.
4. **Exception Handling**: Replaced `requests.exceptions.RequestException` with `urllib3.exceptions.HTTPError` for handling exceptions.
5. **File Uploads**: Since `urllib3` does not natively support file uploads in the same way as `requests`, the `files` parameter was removed. File uploads would need to be handled manually using `multipart/form-data` encoding if required.
6. **Response Handling**: Updated response handling to work with `urllib3.response.HTTPResponse` instead of `requests.Response`.

Below is the modified code:

---

### Modified Code
```python
# -*- coding: utf-8 -*-

import enum
import datetime as dt
import typing
import json

import urllib3

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
        self.session = urllib3.PoolManager()
        self._files = None

    @property
    def files(self):
        return self._files

    def __call__(self, method: RequestMethod, *args, **kwargs) -> urllib3.response.HTTPResponse:
        try:
            headers = kwargs.get('headers', {})
            if self.auth is not None:
                # Add basic auth header if auth is provided
                headers['Authorization'] = f'Basic {self.auth}'

            if self.session is not None:
                response = self.session.request(
                    method=method.value,
                    url=self.url,
                    fields=self.query_parameters(),
                    body=json.dumps(self.body_parameters()),
                    headers=headers
                )
            else:
                # Direct request without session
                http = urllib3.PoolManager()
                response = http.request(
                    method=method.value,
                    url=self.url,
                    fields=self.query_parameters(),
                    body=json.dumps(self.body_parameters()),
                    headers=headers
                )
        except urllib3.exceptions.HTTPError as exc:
            raise pycamunda.PyCamundaException(exc)
        if response.status != 200:
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


def _raise_for_status(response: urllib3.response.HTTPResponse) -> None:
    """Handle http errors regarding Camunda.

    :param response: Response coming from Camunda.
    """
    try:
        message = json.loads(response.data.decode('utf-8')).get('message', '')
    except (KeyError, TypeError, json.decoder.JSONDecodeError):
        message = ''

    if response.status == 400:
        raise pycamunda.BadRequest(message)
    if response.status == 401:
        raise pycamunda.Unauthorized(message)
    elif response.status == 403:
        raise pycamunda.Forbidden(message)
    elif response.status == 404:
        raise pycamunda.NotFound(message)

    raise pycamunda.NoSuccess(response.data.decode('utf-8'))


class _PathMixin:
    @property
    def url(self):
        if self.id_ is not None:
            return self._url.format(path=self.id_)
        if self.tenant_id is not None:
            return self._url.format(path=f'key/{self.key}/tenant-id/{self.tenant_id}')
        return self._url.format(path=f'key/{self.key}')
```

---

### Key Notes:
1. **File Uploads**: The `files` parameter is not directly supported in `urllib3`. If file uploads are required, you would need to manually encode the files using `multipart/form-data`.
2. **Response Handling**: `urllib3.response.HTTPResponse` does not have the same methods as `requests.Response`. For example, `response.data` is used instead of `response.json()` or `response.text`.
3. **Authentication**: Basic authentication is manually added to the headers since `urllib3` does not have a built-in `auth` parameter like `requests`.

This code should now work with `urllib3` version 2.4.0.