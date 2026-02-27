from unittest.mock import MagicMock

import pytest
import pycurl
from io import BytesIO

from pynubank import NuRequestException
from pynubank.utils.http import HttpClient


class MockResponse:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self._content = content

    @property
    def content(self):
        return self._content

    @property
    def text(self):
        return self._content.decode('utf-8')


def mock_pycurl_get(url):
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEFUNCTION, buffer.write)
    curl.perform()
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()
    return MockResponse(status_code, buffer.getvalue())


def mock_pycurl_post(url, data):
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.POST, 1)
    curl.setopt(curl.POSTFIELDS, data)
    curl.setopt(curl.WRITEFUNCTION, buffer.write)
    curl.perform()
    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()
    return MockResponse(status_code, buffer.getvalue())


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
    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(side_effect=lambda url: MockResponse(http_status, b'')))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        client.get('http://some-url')
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status
        assert ex.response.status_code == http_status


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
    monkeypatch.setattr('pynubank.utils.http.post', MagicMock(side_effect=lambda url, data: MockResponse(http_status, b'')))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        client.post('http://some-url', {})
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status
        assert ex.response.status_code == http_status


def test_get(monkeypatch):
    monkeypatch.setattr('pynubank.utils.http.get', MagicMock(return_value=MockResponse(200, b'{"key":123}')))

    client = HttpClient()

    response = client.get('some-url')

    assert response['key'] == 123


def test_post(monkeypatch):
    monkeypatch.setattr('pynubank.utils.http.post', MagicMock(return_value=MockResponse(200, b'{"key":555}')))

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
