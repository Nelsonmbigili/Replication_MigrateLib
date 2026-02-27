### Explanation of Changes
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Import Changes**: Replaced `requests.Response` with `httpx.Response`.
2. **Mocking Changes**: Updated the `monkeypatch` calls to mock `httpx` methods (`httpx.get` and `httpx.post`) instead of `requests`.
3. **Response Content**: In `httpx`, the response content is accessed using `response.content` (similar to `requests`), but the `_content` attribute is not directly modifiable. Instead, we use `httpx.Response`'s constructor to create a mock response with the desired content and status code.
4. **Behavioral Consistency**: Ensured that the behavior of the tests remains consistent with the original `requests` implementation.

### Modified Code
Here is the complete code after migrating to `httpx`:

```python
from unittest.mock import MagicMock

import pytest
from httpx import Response

from pynubank import NuRequestException
from pynubank.utils.http import HttpClient


@pytest.mark.parametrize('http_status', [
    100, 101, 102, 103,
    201, 202, 203, 204, 205, 206, 207, 208, 226,
    300, 301, 302, 303, 304, 305, 306, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422,
    423,
    424, 426, 428, 429, 431, 440, 444, 449, 450, 451, 495, 496, 497, 498, 499,
    500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 530, 598
])
def test_http_get_handler_throws_exception_on_status_different_of_200(monkeypatch, http_status):
    response = Response(status_code=http_status)
    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(return_value=response))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        client.get('http://some-url')
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status
        assert ex.response == response


@pytest.mark.parametrize('http_status', [
    100, 101, 102, 103,
    201, 202, 203, 204, 205, 206, 207, 208, 226,
    300, 301, 302, 303, 304, 305, 306, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422,
    423,
    424, 426, 428, 429, 431, 440, 444, 449, 450, 451, 495, 496, 497, 498, 499,
    500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 530, 598
])
def test_http_post_handler_throws_exception_on_status_different_of_200(monkeypatch, http_status):
    response = Response(status_code=http_status)
    monkeypatch.setattr('pynubank.utils.http.post', MagicMock(return_value=response))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        client.post('http://some-url', {})
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status
        assert ex.response == response


def test_get(monkeypatch):
    response = Response(status_code=200, content=b'{"key":123}')
    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(return_value=response))

    client = HttpClient()

    response = client.get('some-url')

    assert response['key'] == 123


def test_post(monkeypatch):
    response = Response(status_code=200, content=b'{"key":555}')
    monkeypatch.setattr('pynubank.utils.http.post', MagicMock(return_value=response))

    client = HttpClient()

    response = client.post('some-url', {})

    assert response['key'] == 555


def test_client_should_clear_headers_on_new_instance():
    client = HttpClient()
    client.set_header('SomeHeader', 'SomeValue')

    client = HttpClient()
    client.set_header('OtherHeader', 'SomeValue')

    assert client.get_header('SomeHeader') is None
    assert client.get_header('OtherHeader') == 'SomeValue'
```

### Key Points
- The `httpx.Response` constructor is used to create mock responses with the desired `status_code` and `content`.
- The `monkeypatch` calls are updated to mock `httpx` methods (`httpx.get` and `httpx.post`).
- The behavior and structure of the tests remain unchanged to ensure compatibility with the rest of the application.