import json

import aiohttp
from aioresponses import aioresponses
from fastapi.testclient import TestClient
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
def client_fastAPI():
    return TestClient(app=app)


@pytest.mark.asyncio
async def test_query_url(client_aio):
    rst = await SingletonAiohttp.query_url("test/toto")
    assert rst == {"result": 2}


def test_endpoint(client_fastAPI):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))

        result = client_fastAPI.get(url='/endpoint/')
    assert result is not None

    result_json = result.json()
    assert result_json == {'success': 1}


def test_endpoint_multi(client_fastAPI):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))
        mock_server.post(url=url, status=200, body=json.dumps({"success": 2}))

        result = client_fastAPI.get(url='/endpoint_multi/')
    assert result is not None

    result_json = result.json()
    assert result_json == {'success': 3}


@pytest.mark.asyncio
async def test_endpoint_stream(client_fastAPI):
    data = b'TOTO' * 10000

    async with aiohttp.ClientSession() as session:
        async with session.post(url='http://localhost:8080/endpoint_stream/', data=data) as result:
            assert result is not None
            rst = await result.read()
            assert rst == b'RST' + data
