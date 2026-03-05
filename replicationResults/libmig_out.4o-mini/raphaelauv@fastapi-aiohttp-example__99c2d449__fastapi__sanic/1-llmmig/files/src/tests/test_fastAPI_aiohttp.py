import json

import httpx
from aioresponses import aioresponses
from sanic import Sanic
from sanic.response import json as sanic_json
import pytest

from fastAPI_aiohttp.fastAPI import app, SingletonAiohttp

@pytest.fixture
def client_aio():
    with aioresponses() as m:
        m.post(url="test/toto",
               status=200,
               body=json.dumps({"result": 2}))
        yield m

@pytest.fixture
def client_sanic():
    return app.test_client

@pytest.mark.asyncio
async def test_query_url(client_aio):
    rst = await SingletonAiohttp.query_url("test/toto")
    assert rst == {"result": 2}

async def test_endpoint(client_sanic):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))

        request, response = await client_sanic.get(url='/endpoint/')
    assert response is not None

    result_json = response.json
    assert result_json == {'success': 1}

async def test_endpoint_multi(client_sanic):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))
        mock_server.post(url=url, status=200, body=json.dumps({"success": 2}))

        request, response = await client_sanic.get(url='/endpoint_multi/')
    assert response is not None

    result_json = response.json
    assert result_json == {'success': 3}

async def test_endpoint_stream(client_sanic):
    data = b'TOTO' * 10000

    request, response = await client_sanic.post(url='/endpoint_stream/', data=data)
    assert response is not None
    rst = response.body
    assert rst == b'RST' + data
