### Explanation of Changes:
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Import Changes**: Replaced `from requests import Response` with `from httpx import Response` since `httpx` provides a similar `Response` object.
2. **Response Object**: Updated the creation of the `Response` object to use `httpx.Response` instead of `requests.Response`. The `httpx.Response` constructor requires additional arguments (`status_code` and optionally `content`), so these were added where necessary.
3. **Monkeypatching**: Updated the `monkeypatch` calls to ensure compatibility with `httpx`. The `httpx` library's API is similar to `requests`, so no significant changes were needed for mocking HTTP calls.

### Modified Code:
```python
from unittest.mock import MagicMock

import pytest
from httpx import Response

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
    response = Response(status_code=http_status)
    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(return_value=response))

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
    response = Response(status_code=http_status)
    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(return_value=response))

    assert is_alive() == False
```

### Key Notes:
- The `httpx.Response` constructor requires a `status_code` argument, and optionally `content` or `text` for the response body. In this case, only `status_code` was necessary for the tests.
- The rest of the code remains unchanged because `httpx` is designed to be a drop-in replacement for `requests` in most cases.