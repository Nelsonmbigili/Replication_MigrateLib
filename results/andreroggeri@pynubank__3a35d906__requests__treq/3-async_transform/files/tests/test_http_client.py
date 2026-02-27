from unittest.mock import AsyncMock

import pytest
from treq.testing import StubTreq
from twisted.web.http import Response as TwistedResponse
from twisted.web.iweb import IBodyProducer
from twisted.internet.defer import succeed
from zope.interface import implementer

from pynubank import NuRequestException
from pynubank.utils.http import HttpClient


@implementer(IBodyProducer)
class StringProducer:
    def __init__(self, body):
        self.body = body.encode('utf-8')
        self.length = len(self.body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


@pytest.mark.asyncio
@pytest.mark.parametrize('http_status', [
    100, 101, 102, 103,
    201, 202, 203, 204, 205, 206, 207, 208, 226,
    300, 301, 302, 303, 304, 305, 306, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422,
    423,
    424, 426, 428, 429, 431, 440, 444, 449, 450, 451, 495, 496, 497, 498, 499,
    500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 530, 598
])
async def test_http_get_handler_throws_exception_on_status_different_of_200(monkeypatch, http_status):
    async def mock_get(*args, **kwargs):
        response = TwistedResponse((b'HTTP/1.1', http_status, b'OK'))
        response.code = http_status
        return response

    monkeypatch.setattr('pynubank.utils.http.get', AsyncMock(side_effect=mock_get))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        await client.get('http://some-url')
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status


@pytest.mark.asyncio
@pytest.mark.parametrize('http_status', [
    100, 101, 102, 103,
    201, 202, 203, 204, 205, 206, 207, 208, 226,
    300, 301, 302, 303, 304, 305, 306, 307, 308,
    400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422,
    423,
    424, 426, 428, 429, 431, 440, 444, 449, 450, 451, 495, 496, 497, 498, 499,
    500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 520, 521, 522, 523, 524, 525, 526, 527, 530, 598
])
async def test_http_post_handler_throws_exception_on_status_different_of_200(monkeypatch, http_status):
    async def mock_post(*args, **kwargs):
        response = TwistedResponse((b'HTTP/1.1', http_status, b'OK'))
        response.code = http_status
        return response

    monkeypatch.setattr('pynubank.utils.http.post', AsyncMock(side_effect=mock_post))

    client = HttpClient()

    with pytest.raises(NuRequestException) as ex:
        await client.post('http://some-url', {})
        assert ex is not None
        assert ex.url == 'http://some-url'
        assert ex.status_code == http_status


@pytest.mark.asyncio
async def test_get(monkeypatch):
    async def mock_get(*args, **kwargs):
        response = TwistedResponse((b'HTTP/1.1', 200, b'OK'))
        response.code = 200
        response.deliverBody = lambda protocol: protocol.dataReceived(b'{"key":123}')
        return response

    monkeypatch.setattr('pynubank.utils.http.get', AsyncMock(side_effect=mock_get))

    client = HttpClient()

    response = await client.get('some-url')

    assert response['key'] == 123


@pytest.mark.asyncio
async def test_post(monkeypatch):
    async def mock_post(*args, **kwargs):
        response = TwistedResponse((b'HTTP/1.1', 200, b'OK'))
        response.code = 200
        response.deliverBody = lambda protocol: protocol.dataReceived(b'{"key":555}')
        return response

    monkeypatch.setattr('pynubank.utils.http.post', AsyncMock(side_effect=mock_post))

    client = HttpClient()

    response = await client.post('some-url', {})

    assert response['key'] == 555


def test_client_should_clear_headers_on_new_instance():
    client = HttpClient()
    client.set_header('SomeHeader', 'SomeValue')

    client = HttpClient()
    client.set_header('OtherHeader', 'SomeValue')

    assert client.get_header('SomeHeader') is None
    assert client.get_header('OtherHeader') == 'SomeValue'
