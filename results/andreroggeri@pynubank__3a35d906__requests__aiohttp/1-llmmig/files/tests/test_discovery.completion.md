### Explanation of Changes

To migrate the code from `requests` to `aiohttp`, the following changes were made:

1. **`aiohttp` is Asynchronous**: Unlike `requests`, `aiohttp` is an asynchronous library. This means that any HTTP calls made using `aiohttp` must be awaited, and the functions making these calls must be defined as `async`.

2. **Mocking Asynchronous Functions**: Since `aiohttp` uses asynchronous methods, mocking these methods requires using `AsyncMock` instead of `MagicMock`.

3. **Response Object**: The `aiohttp` response object differs from the `requests` response object. For example, the `status` attribute is used instead of `status_code`.

4. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` to make HTTP requests. This session must be properly managed (e.g., using `async with`).

5. **Test Adjustments**: The test functions that interact with `aiohttp` must also be asynchronous (`async def`) and use `pytest.mark.asyncio` to indicate they are asynchronous tests.

Below is the modified code with these changes applied.

---

### Modified Code

```python
from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientResponse

from pynubank import NuException, is_alive
from pynubank.utils.discovery import Discovery
from pynubank.utils.http import HttpClient
from pynubank.utils.mock_http import MockHttpClient

def build_discovery() -> Discovery:
    http = HttpClient()
    discovery = Discovery(http)
    return discovery


@pytest.mark.asyncio
async def test_get_unexistent_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', AsyncMock(return_value=proxy_return))

    discovery = build_discovery()

    with pytest.raises(NuException) as ex:
        await discovery.get_url('some-url')
        assert ex is not None


@pytest.mark.asyncio
async def test_get_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', AsyncMock(return_value=proxy_return))

    discovery = build_discovery()

    assert await discovery.get_url('token') == proxy_return['token']


@pytest.mark.asyncio
async def test_get_app_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', AsyncMock(return_value=proxy_return))

    discovery = build_discovery()

    assert await discovery.get_app_url('lift') == proxy_return['lift']


@pytest.mark.asyncio
@pytest.mark.parametrize('http_status', [
    200, 201
])
async def test_is_alive_if_nubank_server_is_up(monkeypatch, http_status):
    response = AsyncMock(spec=ClientResponse)
    response.status = http_status
    monkeypatch.setattr('pynubank.utils.http.get', AsyncMock(return_value=response))

    assert await is_alive() == True


@pytest.mark.asyncio
@pytest.mark.parametrize('http_status', [
    100, 101, 102, 103,
    202, 203, 204, 205, 206, 207, 208, 226,
    300, 301, 302, 303, 304, 305, 306, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422,
    423,
    424, 426, 428, 429, 431, 440, 444, 449, 450, 451, 495, 496, 497, 498, 499,
    500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 530, 598
])
async def test_is_alive_if_nubank_server_is__down(monkeypatch, http_status):
    response = AsyncMock(spec=ClientResponse)
    response.status = http_status
    monkeypatch.setattr('pynubank.utils.http.get', AsyncMock(return_value=response))

    assert await is_alive() == False
```

---

### Key Changes in the Code

1. **`AsyncMock` for Mocking Asynchronous Functions**:
   - Replaced `MagicMock` with `AsyncMock` for mocking `HttpClient.get` and `pynubank.utils.http.get`.

2. **`pytest.mark.asyncio`**:
   - Added `@pytest.mark.asyncio` to all test functions that involve asynchronous calls.

3. **Awaiting Asynchronous Calls**:
   - Added `await` before calls to `discovery.get_url`, `discovery.get_app_url`, and `is_alive`.

4. **`ClientResponse` Mocking**:
   - Used `AsyncMock` with `spec=ClientResponse` to mock `aiohttp` response objects.
   - Replaced `response.status_code` with `response.status` to match `aiohttp`'s response object.

5. **Test Function Definitions**:
   - Changed test functions to `async def` to support asynchronous operations.

These changes ensure the code is fully migrated to use `aiohttp` while maintaining the original functionality and structure.