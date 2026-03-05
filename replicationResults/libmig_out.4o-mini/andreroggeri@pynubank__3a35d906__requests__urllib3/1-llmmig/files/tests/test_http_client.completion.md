### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import for `Response` from `requests` was removed, as `urllib3` does not have a direct equivalent. Instead, we will create a mock response using `urllib3`'s `HTTPResponse`.
  
2. **Mocking Responses**: The `Response` object from `requests` was replaced with a mock object that simulates the behavior of `urllib3`'s `HTTPResponse`. This includes setting the status code and content appropriately.

3. **Method Calls**: The `get` and `post` methods in the `HttpClient` class are assumed to be using `requests` methods. We will keep the method calls the same, as the `HttpClient` class is part of the larger application and should not be altered.

4. **Response Handling**: The way we access the content of the response was changed to reflect how `urllib3` handles response data.

Here is the modified code:

```python
from unittest.mock import MagicMock
from urllib3 import HTTPResponse
import pytest

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
    response = HTTPResponse(status=http_status)
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
    response = HTTPResponse(status=http_status)
    monkeypatch.setattr('pynubank.utils.http.post', MagicMock(return_value=response))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        client.post('http://some-url', {})
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status
        assert ex.response == response


def test_get(monkeypatch):
    response = HTTPResponse(status=200)
    response.data = b'{"key":123}'
    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(return_value=response))

    client = HttpClient()

    response = client.get('some-url')

    assert response['key'] == 123


def test_post(monkeypatch):
    response = HTTPResponse(status=200)
    response.data = b'{"key":555}'
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

This code now uses `urllib3` for HTTP responses while maintaining the original structure and functionality of the tests.