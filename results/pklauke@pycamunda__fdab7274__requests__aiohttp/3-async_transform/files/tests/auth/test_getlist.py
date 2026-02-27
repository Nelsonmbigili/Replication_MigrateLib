# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.auth
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_getlist_params(engine_url, getlist_input, getlist_output):
    get_authorizations = pycamunda.auth.GetList(url=engine_url, **getlist_input)

    assert get_authorizations.url == engine_url + '/auth'
    assert get_authorizations.query_parameters() == getlist_output
    assert get_authorizations.body_parameters() == {}


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_getlist_calls_requests(mock, engine_url):
    get_authorizations = pycamunda.auth.GetList(url=engine_url)
    get_authorizations()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'GET'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_getlist_raises_pycamunda_exception(engine_url):
    get_authorizations = pycamunda.auth.GetList(url=engine_url)
    with pytest.raises(pycamunda.PyCamundaException):
        get_authorizations()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.auth.Authorization', unittest.mock.MagicMock())
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_getlist_raises_for_status(mock, engine_url):
    get_authorizations = pycamunda.auth.GetList(url=engine_url)
    get_authorizations()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_getlist_returns_authorizations(engine_url):
    get_authorizations = pycamunda.auth.GetList(url=engine_url)
    authorizations = get_authorizations()

    assert isinstance(authorizations, tuple)
    assert all(isinstance(auth, pycamunda.auth.Authorization) for auth in authorizations)
