### Explanation of Changes

The migration from the `requests` library to `urllib3` involves the following changes:
1. **Response Object**: The `requests.Response` object is replaced with `urllib3.response.HTTPResponse`. The `HTTPResponse` object is used to simulate HTTP responses in the tests.
2. **Mocking HTTP Calls**: The `monkeypatch` calls that mock `requests.get` are updated to mock `urllib3.PoolManager.request` instead, as `urllib3` uses `PoolManager` for HTTP requests.
3. **Status Code Handling**: The `HTTPResponse` object in `urllib3` does not have a `status_code` attribute. Instead, the `status` attribute is used to represent the HTTP status code.
4. **Import Changes**: The `requests` import is removed, and `urllib3` is imported instead.

Below is the modified code after migrating to `urllib3`.

---

### Modified Code
```python
from unittest.mock import MagicMock

import pytest
from urllib3.response import HTTPResponse
from urllib3 import PoolManager

from pynubank import NuException, is_alive
from pynubank.utils.discovery import Discovery
from pynubank.utils.http import HttpClient
from pynubank.utils.mock_http import MockHttpClient

def build_discovery() -> Discovery:
    http = HttpClient()
    discovery = Discovery(http)
    return discovery


def test_get_unexistent_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', MagicMock(return_value=proxy_return))

    discovery = build_discovery()

    with pytest.raises(NuException) as ex:
        discovery.get_url('some-url')
        assert ex is not None


def test_get_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', MagicMock(return_value=proxy_return))

    discovery = build_discovery()

    assert discovery.get_url('token') == proxy_return['token']


def test_get_app_url(monkeypatch, proxy_return):
    monkeypatch.setattr(HttpClient, 'get', MagicMock(return_value=proxy_return))

    discovery = build_discovery()

    assert discovery.get_app_url('lift') == proxy_return['lift']

@pytest.mark.parametrize('http_status', [
    200, 201
])
def test_is_alive_if_nubank_server_is_up(monkeypatch, http_status):
    response = HTTPResponse(status=http_status)
    monkeypatch.setattr('pynubank.utils.http.PoolManager.request', MagicMock(return_value=response))

    assert is_alive() == True

@pytest.mark.parametrize('http_status', [
    100, 101, 102, 103,
    202, 203, 204, 205, 206, 207, 208, 226,
    300, 301, 302, 303, 304, 305, 306, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422,
    423,
    424, 426, 428, 429, 431, 440, 444, 449, 450, 451, 495, 496, 497, 498, 499,
    500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 530, 598
])
def test_is_alive_if_nubank_server_is__down(monkeypatch, http_status):
    response = HTTPResponse(status=http_status)
    monkeypatch.setattr('pynubank.utils.http.PoolManager.request', MagicMock(return_value=response))

    assert is_alive() == False
```

---

### Key Points
1. The `Response` object from `requests` is replaced with `HTTPResponse` from `urllib3.response`.
2. The `status_code` attribute is replaced with the `status` attribute in `HTTPResponse`.
3. Mocking is updated to replace `requests.get` with `urllib3.PoolManager.request`.
4. The `requests` import is removed, and `urllib3` is imported where necessary.

This ensures the code now uses `urllib3` version 2.3.0 instead of `requests` version 2.31.0.