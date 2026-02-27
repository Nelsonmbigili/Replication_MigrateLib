# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.externaltask
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_get_params(engine_url):
    get_task = pycamunda.externaltask.Get(url=engine_url, id_='aTaskId')

    assert get_task.url == engine_url + '/external-task/aTaskId'
    assert get_task.query_parameters() == {}
    assert get_task.body_parameters() == {}


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
@unittest.mock.patch('pycamunda.externaltask.ExternalTask', unittest.mock.MagicMock())
async def test_get_calls_requests(mock, engine_url):
    get_task = pycamunda.externaltask.Get(url=engine_url, id_='aTaskId')
    get_task()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'GET'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_get_raises_pycamunda_exception(engine_url):
    get_task = pycamunda.externaltask.Get(url=engine_url, id_='aTaskId')
    with pytest.raises(pycamunda.PyCamundaException):
        get_task()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.externaltask.ExternalTask', unittest.mock.MagicMock())
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_get_raises_for_status(mock, engine_url):
    get_task = pycamunda.externaltask.Get(url=engine_url, id_='aTaskId')
    get_task()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
@unittest.mock.patch('pycamunda.base.from_isoformat', unittest.mock.MagicMock())
async def test_get_returns_none(engine_url):
    get_task = pycamunda.externaltask.Get(url=engine_url, id_='aTaskId')
    task = get_task()

    assert isinstance(task, pycamunda.externaltask.ExternalTask)
