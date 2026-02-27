# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.caseinst
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_close_params(engine_url):
    close_instance = pycamunda.caseinst.Close(url=engine_url, id_='anId', deletions=['aVar'])
    close_instance.add_variable(
        name='anotherVar', type_='String', value='aVal', value_info={}, local=True
    )

    assert close_instance.url == engine_url + '/case-instance/anId/close'
    assert close_instance.query_parameters() == {}
    assert close_instance.body_parameters() == {
        'deletions': [{'name': 'aVar'}],
        'variables': {
            'anotherVar': {'value': 'aVal', 'type': 'String', 'valueInfo': {}, 'local': True}
        }
    }


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_close_calls_requests(mock, engine_url):
    close_instance = pycamunda.caseinst.Close(url=engine_url, id_='anId')
    close_instance()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'POST'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_close_raises_pycamunda_exception(engine_url):
    close_instance = pycamunda.caseinst.Close(url=engine_url, id_='anId')
    with pytest.raises(pycamunda.PyCamundaException):
        close_instance()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_close_raises_for_status(mock, engine_url):
    close_instance = pycamunda.caseinst.Close(url=engine_url, id_='anId')
    close_instance()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_close_returns_none(engine_url):
    close_instance = pycamunda.caseinst.Close(url=engine_url, id_='anId')
    result = close_instance()

    assert result is None
