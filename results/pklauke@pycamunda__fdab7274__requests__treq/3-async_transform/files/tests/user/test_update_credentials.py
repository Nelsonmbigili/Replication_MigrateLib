# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.base
import pycamunda.user
import pycamunda.resource
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_update_credentials_params(engine_url, update_credentials_input):
    update_credentials = pycamunda.user.UpdateCredentials(
        url=engine_url, **update_credentials_input
    )

    assert update_credentials.url == engine_url + '/user/janedoe/credentials'
    assert update_credentials.query_parameters() == {}
    assert update_credentials.body_parameters() == {
        'password': 'password',
        'authenticatedUserPassword': 'password'
    }


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_update_credentials_calls_requests(mock, engine_url, update_credentials_input):
    update_credentials = pycamunda.user.UpdateCredentials(
        url=engine_url, **update_credentials_input
    )
    update_credentials()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'PUT'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_update_credentials_raises_pycamunda_exception(engine_url, update_credentials_input):
    update_credentials = pycamunda.user.UpdateCredentials(
        url=engine_url, **update_credentials_input
    )
    with pytest.raises(pycamunda.PyCamundaException):
        update_credentials()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_update_credentials_raises_for_status(mock, engine_url, update_credentials_input):
    update_credentials = pycamunda.user.UpdateCredentials(
        url=engine_url, **update_credentials_input
    )
    update_credentials()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_update_credentials_returns_none(engine_url, update_credentials_input):
    update_credentials = pycamunda.user.UpdateCredentials(
        url=engine_url, **update_credentials_input
    )
    result = update_credentials()

    assert result is None
