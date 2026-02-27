### Explanation of Changes:
To migrate the code from using the `httpx` library to the `requests` library, the following changes were made:
1. **Replace `httpx.Response` with `requests.Response`**: The `httpx.Response` type was replaced with `requests.Response` where applicable.
2. **Replace `httpx`-specific methods with `requests` equivalents**:
   - The `client_fastAPI.get()` and `client_fastAPI.stream()` methods were left unchanged because they are part of the `TestClient` from FastAPI, not `httpx`.
   - The `httpx.Response` object was replaced with `requests.Response` in the `test_endpoint` and `test_endpoint_multi` functions.
3. **No changes to `aioresponses` or `TestClient`**: These are unrelated to `httpx` and remain unchanged.

### Modified Code:
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

    with client_fastAPI.stream('POST', url='/endpoint_stream/', content=data) as result:
        assert result is not None
        result.read()
        rst = result.content
        assert rst == b'RST' + data
```

### Summary of Changes:
- Replaced `httpx.Response` with `requests.Response` in the `test_endpoint` and `test_endpoint_multi` functions.
- No changes were made to `TestClient` or `aioresponses` as they are unrelated to `httpx`.
- The rest of the code remains unchanged to ensure compatibility with the existing application.