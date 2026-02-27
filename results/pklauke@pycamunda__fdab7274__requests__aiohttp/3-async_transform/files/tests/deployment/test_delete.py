# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.deployment
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_delete_params(engine_url):
    delete_deployment = pycamunda.deployment.Delete(
        url=engine_url, id_='anId', cascade=True, skip_custom_listeners=True, skip_io_mappings=True
    )

    assert delete_deployment.url == engine_url + '/deployment/anId'
    assert delete_deployment.query_parameters() == {
        'cascade': 'true', 'skipCustomListeners': 'true', 'skipIoMappings': 'true'
    }
    assert delete_deployment.body_parameters() == {}


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_get_calls_requests(mock, engine_url):
    delete_deployment = pycamunda.deployment.Delete(url=engine_url, id_='anId')
    delete_deployment()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'DELETE'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_get_raises_pycamunda_exception(engine_url):
    delete_deployment = pycamunda.deployment.Delete(url=engine_url, id_='anId')
    with pytest.raises(pycamunda.PyCamundaException):
        delete_deployment()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_get_raises_for_status(mock, engine_url):
    delete_deployment = pycamunda.deployment.Delete(url=engine_url, id_='anId')
    delete_deployment()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_get_returns_none(engine_url):
    delete_deployment = pycamunda.deployment.Delete(url=engine_url, id_='anId')
    result = delete_deployment()

    assert result is None
