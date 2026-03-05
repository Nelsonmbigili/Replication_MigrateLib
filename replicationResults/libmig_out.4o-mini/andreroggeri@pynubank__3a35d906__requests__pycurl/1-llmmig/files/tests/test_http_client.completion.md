### Explanation of Changes

To migrate the code from using the `requests` library to using `pycurl`, the following changes were made:

1. **Importing PyCurl**: The `requests` library was replaced with `pycurl`. The `Response` object from `requests` is not directly applicable in `pycurl`, so we need to handle the response differently.
  
2. **Mocking HTTP Methods**: The `get` and `post` methods were modified to use `pycurl` for making HTTP requests. This involves setting up a `pycurl.Curl` object, configuring it with the appropriate options, and handling the response manually.

3. **Response Handling**: Since `pycurl` does not return a `Response` object, we need to create a custom response handling mechanism to capture the HTTP status code and response body.

4. **Error Handling**: The exception handling remains the same, but we need to ensure that the status code and response body are correctly captured from the `pycurl` response.

Here is the modified code:

```python
from unittest.mock import MagicMock
import pytest
import pycurl
from io import BytesIO

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
    class MockCurl:
        def __init__(self):
            self.response_code = http_status
            self.response_data = b''

        def perform(self):
            pass

        def getinfo(self, info):
            if info == pycurl.RESPONSE_CODE:
                return self.response_code
            return None

        def setopt(self, option, value):
            if option == pycurl.WRITEFUNCTION:
                self.write_function = value

        def write(self, data):
            self.response_data += data

    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(return_value=MockCurl()))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        client.get('http://some-url')
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status
        assert ex.response == b''


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
    class MockCurl:
        def __init__(self):
            self.response_code = http_status
            self.response_data = b''

        def perform(self):
            pass

        def getinfo(self, info):
            if info == pycurl.RESPONSE_CODE:
                return self.response_code
            return None

        def setopt(self, option, value):
            if option == pycurl.WRITEFUNCTION:
                self.write_function = value

        def write(self, data):
            self.response_data += data

    monkeypatch.setattr('pynubank.utils.http.post', MagicMock(return_value=MockCurl()))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        client.post('http://some-url', {})
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status
        assert ex.response == b''


def test_get(monkeypatch):
    class MockCurl:
        def __init__(self):
            self.response_code = 200
            self.response_data = b'{"key":123}'

        def perform(self):
            pass

        def getinfo(self, info):
            if info == pycurl.RESPONSE_CODE:
                return self.response_code
            return None

        def setopt(self, option, value):
            if option == pycurl.WRITEFUNCTION:
                self.write_function = value

        def write(self, data):
            self.response_data += data

    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(return_value=MockCurl()))

    client = HttpClient()

    response = client.get('some-url')

    assert response['key'] == 123


def test_post(monkeypatch):
    class MockCurl:
        def __init__(self):
            self.response_code = 200
            self.response_data = b'{"key":555}'

        def perform(self):
            pass

        def getinfo(self, info):
            if info == pycurl.RESPONSE_CODE:
                return self.response_code
            return None

        def setopt(self, option, value):
            if option == pycurl.WRITEFUNCTION:
                self.write_function = value

        def write(self, data):
            self.response_data += data

    monkeypatch.setattr('pynubank.utils.http.post', MagicMock(return_value=MockCurl()))

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

This code now uses `pycurl` for HTTP requests while maintaining the original structure and logic of the tests.