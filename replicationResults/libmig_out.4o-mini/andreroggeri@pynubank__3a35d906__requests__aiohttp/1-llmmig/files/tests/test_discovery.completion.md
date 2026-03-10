### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Importing aiohttp**: The `aiohttp` library was imported to handle asynchronous HTTP requests.
2. **Asynchronous Functions**: The functions that make HTTP requests were modified to be asynchronous. This includes using `async def` for the function definitions and `await` for calling the HTTP methods.
3. **Mocking Asynchronous Calls**: The mocking of HTTP calls was adjusted to accommodate the asynchronous nature of `aiohttp`. This involved using `AsyncMock` instead of `MagicMock` for mocking asynchronous methods.
4. **Response Handling**: The way responses are handled was updated to reflect the `aiohttp` response structure.

Here is the modified code:

```python
from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientResponse

from pynubank import NuException, is_alive
from pynubank.utils.discovery import Discovery
from pynubank.utils.http import HttpClient
from pynubank.utils.mock_http import MockHttpClient

async def build_discovery() -> Discovery:
    http = HttpClient()
    discovery = Discovery(http)
    return discovery


@pytest.mark.asyncio
async def test_get_unexistent_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', AsyncMock(return_value=proxy_return))

    discovery = await build_discovery()

    with pytest.raises(NuException) as ex:
        await discovery.get_url('some-url')
        assert ex is not None


@pytest.mark.asyncio
async def test_get_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', AsyncMock(return_value=proxy_return))

    discovery = await build_discovery()

    assert await discovery.get_url('token') == proxy_return['token']


@pytest.mark.asyncio
async def test_get_app_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', AsyncMock(return_value=proxy_return))

    discovery = await build_discovery()

    assert await discovery.get_app_url('lift') == proxy_return['lift']

@pytest.mark.parametrize('http_status', [
    200, 201
])
@pytest.mark.asyncio
async def test_is_alive_if_nubank_server_is_up(monkeypatch, http_status):
    response = ClientResponse('GET', 'http://test.com')
    response.status = http_status
    monkeypatch.setattr('pynubank.utils.http.get', AsyncMock(return_value=response))

    assert await is_alive() == True

@pytest.mark.parametrize('http_status', [
    100, 101, 102, 103,
    202, 203, 204, 205, 206, 207, 208, 226,
    300, 301, 302, 303, 304, 305, 306, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422,
    423,
    424, 426, 428, 429, 431, 440, 444, 449, 450, 451, 495, 496, 497, 498, 499,
    500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 530, 598
])
@pytest.mark.asyncio
async def test_is_alive_if_nubank_server_is__down(monkeypatch, http_status):
    response = ClientResponse('GET', 'http://test.com')
    response.status = http_status
    monkeypatch.setattr('pynubank.utils.http.get', AsyncMock(return_value=response))

    assert await is_alive() == False
```

### Note
- The `@pytest.mark.asyncio` decorator is used to indicate that the test functions are asynchronous.
- The `ClientResponse` is used to create a mock response object that mimics the behavior of an `aiohttp` response.