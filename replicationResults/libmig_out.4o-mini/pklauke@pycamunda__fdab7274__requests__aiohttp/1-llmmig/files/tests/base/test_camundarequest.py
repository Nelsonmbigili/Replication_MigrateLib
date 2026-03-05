# -*- coding: utf-8 -*-

import unittest.mock
import aiohttp
import asyncio

from aiohttp import ClientSession, BasicAuth


async def test_camundarequest_keeps_query_params(engine_url, MyRequest):
    assert MyRequest(url=engine_url, query_param='aStr').query_parameters()['param'] == 'aStr'
    assert MyRequest(url=engine_url, query_param=1).query_parameters()['param'] == 1


async def test_camundarequest_keeps_body_params(engine_url, MyRequest):
    assert MyRequest(url=engine_url, body_param='aStr').body_parameters()['param'] == 'aStr'
    assert MyRequest(url=engine_url, body_param=1).body_parameters()['param'] == 1
    assert MyRequest(url=engine_url, body_param=True).body_parameters()['param'] is True
    assert MyRequest(url=engine_url, body_param=False).body_parameters()['param'] is False


async def test_camundarequest_converts_bool_query_params(engine_url, MyRequest):
    assert MyRequest(url=engine_url, query_param=True).query_parameters()['param'] == 'true'
    assert MyRequest(url=engine_url, query_param=False).query_parameters()['param'] == 'false'


async def test_camundarequest_converts_datetime_params(
    engine_url, MyRequest, date, date_tz, date_str, date_tz_str
):
    assert MyRequest(url=engine_url, query_param=date).query_parameters()['param'] == date_str
    assert MyRequest(url=engine_url, query_param=date_tz).query_parameters()['param'] == date_tz_str

    assert MyRequest(url=engine_url, body_param=date).body_parameters()['param'] == date_str
    assert MyRequest(url=engine_url, body_param=date_tz).body_parameters()['param'] == date_tz_str


@unittest.mock.patch('aiohttp.ClientSession.request')
async def test_camundarequest_session(mock, engine_url, MyRequest):
    request = MyRequest(url=engine_url)
    auth = BasicAuth(username='Jane', password='password')

    async with ClientSession() as session:
        session.auth = auth
        request.session = session

        await request()

        assert mock.called
        assert request.session.auth.username == 'Jane'
        assert request.session.auth.password == 'password'
