import json

import urllib3
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

        http = urllib3.PoolManager()
        response = http.request('GET', 'http://localhost:8080/endpoint/')
        assert response is not None

        result_json = json.loads(response.data.decode('utf-8'))
        assert result_json == {'success': 1}


def test_endpoint_multi(client_fastAPI):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))
        mock_server.post(url=url, status=200, body=json.dumps({"success": 2}))

        http = urllib3.PoolManager()
        response = http.request('GET', 'http://localhost:8080/endpoint_multi/')
        assert response is not None

        result_json = json.loads(response.data.decode('utf-8'))
        assert result_json == {'success': 3}


def test_endpoint_stream(client_fastAPI):
    data = b'TOTO' * 10000

    http = urllib3.PoolManager()
    response = http.request(
        'POST',
        'http://localhost:8080/endpoint_stream/',
        body=data,
        preload_content=False
    )
    assert response is not None
    rst = response.read()
    response.release_conn()
    assert rst == b'RST' + data
