# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.externaltask
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_setpriority_params(engine_url):
    set_priority = pycamunda.externaltask.SetPriority(url=engine_url, id_='anId', priority=10)

    assert set_priority.url == engine_url + '/external-task/anId/priority'
    assert set_priority.query_parameters() == {}
    assert set_priority.body_parameters() == {'priority': 10}


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_setpriority_calls_requests(mock, engine_url):
    set_priority = pycamunda.externaltask.SetPriority(url=engine_url, id_='anId', priority=10)
    set_priority()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'PUT'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_setpriority_raises_pycamunda_exception(engine_url):
    set_priority = pycamunda.externaltask.SetPriority(url=engine_url, id_='anId', priority=10)
    with pytest.raises(pycamunda.PyCamundaException):
        set_priority()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_setpriority_raises_for_status(mock, engine_url):
    set_priority = pycamunda.externaltask.SetPriority(url=engine_url, id_='anId', priority=10)
    set_priority()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_setpriority_returns_none(engine_url):
    set_priority = pycamunda.externaltask.SetPriority(url=engine_url, id_='anId', priority=10)
    result = set_priority()

    assert result is None
