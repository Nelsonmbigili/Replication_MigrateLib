The following Python code currently uses the library "fastapi" version 0.115.12.
Migrate this code to use the library "sanic" version 25.3.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "fastapi" to "sanic".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "fastapi" and "sanic".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import json

import httpx
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

        result: httpx.Response = client_fastAPI.get(url='/endpoint/')
    assert result is not None

    result_json = result.json()
    assert result_json == {'success': 1}


def test_endpoint_multi(client_fastAPI):
    url = "http://localhost:8080/test"
    with aioresponses() as mock_server:
        mock_server.post(url=url, status=200, body=json.dumps({"success": 1}))
        mock_server.post(url=url, status=200, body=json.dumps({"success": 2}))

        result: httpx.Response = client_fastAPI.get(url='/endpoint_multi/')
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