# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.task
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_delegate_params(engine_url):
    delegate_task = pycamunda.task.Delegate(url=engine_url, id_='anId', user_id='anUserId')

    assert delegate_task.url == engine_url + '/task/anId/delegate'
    assert delegate_task.query_parameters() == {}
    assert delegate_task.body_parameters() == {'userId': 'anUserId'}


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_delegate_calls_requests(mock, engine_url):
    delegate_task = pycamunda.task.Delegate(url=engine_url, id_='anId', user_id='anUserId')
    delegate_task()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'POST'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_delegate_raises_pycamunda_exception(engine_url):
    delegate_task = pycamunda.task.Delegate(url=engine_url, id_='anId', user_id='anUserId')
    with pytest.raises(pycamunda.PyCamundaException):
        delegate_task()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_delegate_raises_for_status(mock, engine_url):
    delegate_task = pycamunda.task.Delegate(url=engine_url, id_='anId', user_id='anUserId')
    delegate_task()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_delegate_returns_none(engine_url):
    delegate_task = pycamunda.task.Delegate(url=engine_url, id_='anId', user_id='anUserId')
    result = delegate_task()

    assert result is None
