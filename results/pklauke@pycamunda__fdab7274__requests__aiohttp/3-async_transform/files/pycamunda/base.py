# -*- coding: utf-8 -*-

import enum
import datetime as dt
import typing
import json

import aiohttp

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

    async def __call__(self, method: RequestMethod, *args, **kwargs) -> aiohttp.ClientResponse:
        try:
            if self.session is not None:
                kwargs = {}
                if self.auth is not None:
                    kwargs['auth'] = aiohttp.BasicAuth(*self.auth)
                async with self.session.request(
                    method=method.value,
                    url=self.url,
                    params=self.query_parameters(),
                    json=self.body_parameters(),
                    data=self._prepare_files(),
                    **kwargs
                ) as response:
                    await self._raise_for_status(response)
                    return response
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method.value,
                        url=self.url,
                        params=self.query_parameters(),
                        json=self.body_parameters(),
                        auth=aiohttp.BasicAuth(*self.auth) if self.auth else None,
                        data=self._prepare_files()
                    ) as response:
                        await self._raise_for_status(response)
                        return response
        except aiohttp.ClientError as exc:
            raise pycamunda.PyCamundaException(exc)

    def body_parameters(self, apply: typing.Callable = ...):
        if apply is Ellipsis:
            return super().body_parameters(apply=prepare)
        return super().body_parameters(apply=apply)

    def query_parameters(self, apply: typing.Callable = ...):
        if apply is Ellipsis:
            return super().query_parameters(apply=query_prepare)
        return super().query_parameters(apply=apply)

    def _prepare_files(self):
        """Prepare files for aiohttp."""
        if not self.files:
            return None
        form_data = aiohttp.FormData()
        for key, file in self.files.items():
            form_data.add_field(
                name=key,
                value=file,
                filename=getattr(file, 'name', None),
                content_type='application/octet-stream'
            )
        return form_data

    async def _raise_for_status(self, response: aiohttp.ClientResponse) -> None:
        """Handle http errors regarding Camunda."""
        try:
            message = (await response.json()).get('message', '')
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

        if response.status >= 400:
            raise pycamunda.NoSuccess(await response.text())


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


class _PathMixin:
    @property
    def url(self):
        if self.id_ is not None:
            return self._url.format(path=self.id_)
        if self.tenant_id is not None:
            return self._url.format(path=f'key/{self.key}/tenant-id/{self.tenant_id}')
        return self._url.format(path=f'key/{self.key}')
