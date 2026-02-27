# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.group
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_getlist_params(engine_url, getlist_input, getlist_output):
    get_groups = pycamunda.group.GetList(url=engine_url, **getlist_input)

    assert get_groups.url == engine_url + '/group'
    assert get_groups.query_parameters() == getlist_output
    assert get_groups.body_parameters() == {}


@pytest.mark.asyncio
@unittest.mock.patch('pycamunda.group.Group.load', unittest.mock.MagicMock())
@unittest.mock.patch('requests.Session.request')
async def test_getlist_calls_requests(mock, engine_url):
    get_groups = pycamunda.group.GetList(url=engine_url)
    get_groups()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'GET'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_getlist_raises_pycamunda_exception(engine_url):
    get_groups = pycamunda.group.GetList(url=engine_url)
    with pytest.raises(pycamunda.PyCamundaException):
        get_groups()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.group.Group', unittest.mock.MagicMock())
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_getlist_raises_for_status(mock, engine_url):
    get_groups = pycamunda.group.GetList(url=engine_url)
    get_groups()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_getlist_returns_incident(engine_url):
    get_groups = pycamunda.group.GetList(url=engine_url)
    groups = get_groups()

    assert isinstance(groups, tuple)
    assert all(isinstance(group, pycamunda.group.Group) for group in groups)
