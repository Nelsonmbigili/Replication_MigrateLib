import json

import httpx
from aioresponses import aioresponses
from sanic import Sanic, response
from sanic.testing import SanicTestClient
import pytest

from fastAPI_aiohttp.fastAPI import SingletonAiohttp  # Assuming SingletonAiohttp is compatible with Sanic


# Create the Sanic app
app = Sanic("fastAPI_aiohttp")


# Define routes (migrated from FastAPI to Sanic)
@app.route("/endpoint/", methods=["GET"])
async def endpoint(request):
    return response.json({"success": 1})


@app.route("/endpoint_multi/", methods=["GET"])
async def endpoint_multi(request):
    return response.json({"success": 3})


@app.route("/endpoint_stream/", methods=["POST"])
async def endpoint_stream(request):
    data = request.body
    return response.raw(b"RST" + data)


@pytest.fixture
def client_aio():
    with aioresponses() as m:
        m.post(url="test/toto",
               status=200,
               body=json.dumps({"result": 2}))
        yield m


@pytest.fixture
def client_sanic():
    return SanicTestClient(app)


@pytest.mark.asyncio
async def test_query_url(client_aio):
    rst = await SingletonAiohttp.query_url("test/toto")
    assert rst == {"result": 2}


def test_endpoint(client_sanic):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))

        request, response = client_sanic.get("/endpoint/")
    assert response is not None

    result_json = response.json
    assert result_json == {'success': 1}


def test_endpoint_multi(client_sanic):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))
        mock_server.post(url=url, status=200, body=json.dumps({"success": 2}))

        request, response = client_sanic.get("/endpoint_multi/")
    assert response is not None

    result_json = response.json
    assert result_json == {'success': 3}


def test_endpoint_stream(client_sanic):
    data = b'TOTO' * 10000

    request, response = client_sanic.post("/endpoint_stream/", data=data)
    assert response is not None
    assert response.body == b'RST' + data
