# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import pycamunda.batch
from tests.mock import raise_requests_exception_mock, not_ok_response_mock


def test_get_params(engine_url):
    get_batch = pycamunda.batch.Get(url=engine_url, id_='anId')

    assert get_batch.url == engine_url + '/batch/anId'
    assert get_batch.query_parameters() == {}
    assert get_batch.body_parameters() == {}


def test_get_path(engine_url):
    get_batch = pycamunda.batch.Get(url=engine_url, id_='anId')

    assert get_batch.url == engine_url + '/batch/anId'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request')
async def test_get_calls_requests(mock, engine_url):
    get_batch = pycamunda.batch.Get(url=engine_url, id_='anId')
    get_batch()

    assert mock.called
    assert mock.call_args[1]['method'].upper() == 'GET'


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', raise_requests_exception_mock)
async def test_get_raises_pycamunda_exception(engine_url):
    get_batch = pycamunda.batch.Get(url=engine_url, id_='anId')
    with pytest.raises(pycamunda.PyCamundaException):
        get_batch()


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', not_ok_response_mock)
@unittest.mock.patch('pycamunda.batch.Batch', unittest.mock.MagicMock())
@unittest.mock.patch('pycamunda.base._raise_for_status')
async def test_get_raises_for_status(mock, engine_url):
    get_batch = pycamunda.batch.Get(url=engine_url, id_='anId')
    get_batch()

    assert mock.called


@pytest.mark.asyncio
@unittest.mock.patch('requests.Session.request', unittest.mock.MagicMock())
async def test_get_returns_batch(engine_url):
    get_batch = pycamunda.batch.Get(url=engine_url, id_='anId')
    batch = get_batch()

    assert isinstance(batch, pycamunda.batch.Batch)
