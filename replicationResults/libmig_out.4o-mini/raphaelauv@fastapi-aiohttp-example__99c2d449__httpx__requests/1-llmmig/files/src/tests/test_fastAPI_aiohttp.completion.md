### Explanation of Changes
To migrate the code from using the `httpx` library to the `requests` library, the following changes were made:

1. **Import Statement**: The import for `httpx` was removed, as it is no longer needed.
2. **Response Type**: The type hint for the response variable was changed from `httpx.Response` to `requests.Response`.
3. **Client Method Changes**: The `client_fastAPI.get()` method was used directly without needing to specify the response type, as `requests` does not have an asynchronous context like `httpx`.
4. **Stream Handling**: The `client_fastAPI.stream()` method was replaced with `client_fastAPI.post()` to send data, as `requests` does not have a `stream` method in the same way `httpx` does. The response handling was adjusted accordingly.

### Modified Code
```python
import json

import requests
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

        result: requests.Response = client_fastAPI.get(url='/endpoint/')
    assert result is not None

    result_json = result.json()
    assert result_json == {'success': 1}


def test_endpoint_multi(client_fastAPI):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))
        mock_server.post(url=url, status=200, body=json.dumps({"success": 2}))

        result: requests.Response = client_fastAPI.get(url='/endpoint_multi/')
    assert result is not None

    result_json = result.json()
    assert result_json == {'success': 3}


def test_endpoint_stream(client_fastAPI):
    data = b'TOTO' * 10000

    result = client_fastAPI.post(url='/endpoint_stream/', content=data)
    assert result is not None
    rst = result.content
    assert rst == b'RST' + data
```