# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.task
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_localvariablesdelete_params(engine_url):
    delete_var = pycamunda.task.LocalVariablesDelete(
        url=engine_url, task_id='anId', var_name='aVar'
    )

    assert delete_var.url == engine_url + '/task/anId/localVariables/aVar'
    assert delete_var.query_parameters() == {}
    assert delete_var.body_parameters() == {}


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_localvariablesdelete_calls_requests(mock, engine_url):
    delete_var = pycamunda.task.LocalVariablesDelete(
        url=engine_url, task_id='anId', var_name='aVar'
    )
    delete_var()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'DELETE'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_localvariablesdelete_raises_pycamunda_exception(engine_url):
    delete_var = pycamunda.task.LocalVariablesDelete(
        url=engine_url, task_id='anId', var_name='aVar'
    )
    with pytest.raises(pycamunda.PyCamundaException):
        delete_var()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_localvariablesdelete_raises_for_status(mock, engine_url):
    delete_var = pycamunda.task.LocalVariablesDelete(
        url=engine_url, task_id='anId', var_name='aVar'
    )
    delete_var()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_localvariablesdelete_returns_none(engine_url):
    delete_var = pycamunda.task.LocalVariablesDelete(
        url=engine_url, task_id='anId', var_name='aVar'
    )
    result = delete_var()

    assert result is None
