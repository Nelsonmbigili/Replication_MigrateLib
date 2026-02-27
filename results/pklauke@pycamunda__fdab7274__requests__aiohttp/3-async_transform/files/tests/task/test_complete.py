# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.task
import pycamunda.variable
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def mock_post_with_variables_in_return(*args, json=None, **kwargs):
    class Response:
        def json(self):
            return json['variables']

    return Response()


def test_complete_params(engine_url):
    complete_task = pycamunda.task.Complete(
        url=engine_url, id_='anId', with_variables_in_return=True
    )
    complete_task.add_variable(name='aVar', value='aVal', type_='String', value_info='')

    assert complete_task.url == engine_url + '/task/anId/complete'
    assert complete_task.query_parameters() == {}
    assert complete_task.body_parameters() == {
        'variables': {'aVar': {'value': 'aVal', 'type': 'String', 'valueInfo': ''}},
        'withVariablesInReturn': True
    }


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_complete_calls_requests(mock, engine_url):
    complete_task = pycamunda.task.Complete(url=engine_url, id_='anId')
    complete_task()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'POST'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_complete_raises_pycamunda_exception(engine_url):
    complete_task = pycamunda.task.Complete(url=engine_url, id_='anId')
    with pytest.raises(pycamunda.PyCamundaException):
        complete_task()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_complete_raises_for_status(mock, engine_url):
    complete_task = pycamunda.task.Complete(url=engine_url, id_='anId')
    complete_task()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_complete_returns_none(engine_url):
    complete_task = pycamunda.task.Complete(url=engine_url, id_='anId')
    result = complete_task()

    assert result is None


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', mock_post_with_variables_in_return)
async def test_complete_returns_variables(engine_url):
    complete_task = pycamunda.task.Complete(
        url=engine_url, id_='anId', with_variables_in_return=True
    )
    complete_task.add_variable(name='aVar', value='aVal')
    variables = complete_task()

    assert isinstance(variables, dict)
    assert 'aVar' in variables
    assert all(isinstance(variable, pycamunda.variable.Variable) for variable in variables.values())
    assert variables['aVar'].value == 'aVal'
