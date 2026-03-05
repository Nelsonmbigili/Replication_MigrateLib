# -*- coding: utf-8 -*-

import enum
import datetime as dt
import typing
import json
import pycurl
from io import BytesIO

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

    def __call__(self, method: RequestMethod, *args, **kwargs) -> str:
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(curl.URL, self.url)
            curl.setopt(curl.WRITEFUNCTION, buffer.write)
            curl.setopt(curl.CUSTOMREQUEST, method.value)

            if self.auth is not None:
                curl.setopt(curl.USERPWD, self.auth)

            if self.query_parameters():
                curl.setopt(curl.POSTFIELDS, self.query_parameters())

            if self.body_parameters():
                curl.setopt(curl.POSTFIELDS, json.dumps(self.body_parameters()))

            curl.perform()
            response_code = curl.getinfo(curl.RESPONSE_CODE)
            response_body = buffer.getvalue().decode('utf-8')

            if response_code != 200:
                _raise_for_status(response_code, response_body)

            return response_body

        except pycurl.error as exc:
            raise pycamunda.PyCamundaException(exc)
        finally:
            curl.close()

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


def _raise_for_status(response_code: int, response_body: str) -> None:
    """Handle http errors regarding Camunda.

    :param response_code: Response code coming from Camunda.
    :param response_body: Response body coming from Camunda.
    """
    try:
        message = json.loads(response_body)['message']
    except (KeyError, TypeError, json.decoder.JSONDecodeError):
        message = ''

    if response_code == 400:
        raise pycamunda.BadRequest(message)
    if response_code == 401:
        raise pycamunda.Unauthorized(message)
    elif response_code == 403:
        raise pycamunda.Forbidden(message)
    elif response_code == 404:
        raise pycamunda.NotFound(message)

    raise pycamunda.NoSuccess(response_body)


class _PathMixin:
    @property
    def url(self):
        if self.id_ is not None:
            return self._url.format(path=self.id_)
        if self.tenant_id is not None:
            return self._url.format(path=f'key/{self.key}/tenant-id/{self.tenant_id}')
        return self._url.format(path=f'key/{self.key}')
