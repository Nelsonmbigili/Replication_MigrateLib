### Explanation of Changes

The original code uses the `requests` library for HTTP operations, which is being replaced with the `pycurl` library. The `pycurl` library operates at a lower level than `requests`, requiring more explicit handling of HTTP requests and responses. The following changes were made:

1. **Replaced `requests.Response`**: Since `pycurl` does not have a `Response` object like `requests`, I replaced it with a custom mock response object that mimics the behavior of `requests.Response` for testing purposes.
2. **Modified Mocking**: The `monkeypatch` calls that mock `requests.get` were updated to mock `pycurl`-based HTTP calls.
3. **Custom HTTP Client**: Since `pycurl` requires explicit setup for HTTP requests, I created a helper function to simulate HTTP requests and responses using `pycurl`.
4. **Status Code Handling**: The `pycurl` library does not directly provide a `status_code` attribute. Instead, the HTTP status code is retrieved using `curl.getinfo(pycurl.RESPONSE_CODE)`.

Below is the modified code.

---

### Modified Code
```python
from unittest.mock import MagicMock

import pytest
import pycurl
from io import BytesIO

from pynubank import NuException, is_alive
from pynubank.utils.discovery import Discovery
from pynubank.utils.http import HttpClient
from pynubank.utils.mock_http import MockHttpClient


class MockResponse:
    """A mock response object to simulate pycurl responses."""
    def __init__(self, status_code):
        self.status_code = status_code


def pycurl_request(url):
    """Simulates an HTTP GET request using pycurl and returns a mock response."""
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    curl.perform()
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()
    return MockResponse(status_code)


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
    # Mock the pycurl_request function to return a response with the desired status code
    monkeypatch.setattr('pynubank.utils.http.pycurl_request', MagicMock(return_value=MockResponse(http_status)))

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
    # Mock the pycurl_request function to return a response with the desired status code
    monkeypatch.setattr('pynubank.utils.http.pycurl_request', MagicMock(return_value=MockResponse(http_status)))

    assert is_alive() == False
```

---

### Key Notes:
1. **MockResponse Class**: This class was introduced to simulate the `Response` object from `requests`. It only includes the `status_code` attribute, which is sufficient for the tests.
2. **pycurl_request Function**: This function performs an HTTP GET request using `pycurl` and returns a `MockResponse` object with the HTTP status code.
3. **Monkeypatching**: The `monkeypatch` calls were updated to mock the `pycurl_request` function instead of `requests.get`.

This approach ensures that the code is migrated to use `pycurl` while maintaining the original structure and functionality.