import json
from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientResponse

from pynubank import NuException, MockHttpClient
from pynubank.utils.certificate_generator import CertificateGenerator
from pynubank.utils.discovery import Discovery

headers = {
    'WWW-Authenticate': 'device-authorization encrypted-code="abc123", sent-to="john@doe"'
}


def fake_update_proxy(self: Discovery):
    self.proxy_list_app_url = {
        'gen_certificate': 'https://some-url/gen-cert',
    }


def mock_response(content=None, return_headers=None, status_code=200):
    """
    Mock an aiohttp.ClientResponse-like object.
    """
    response = AsyncMock(spec=ClientResponse)
    response.status = status_code
    response.headers = return_headers or {}
    if content:
        response.text = AsyncMock(return_value=json.dumps(content))
        response.json = AsyncMock(return_value=content)
    else:
        response.text = AsyncMock(return_value="")
        response.json = AsyncMock(return_value=None)

    return response


@pytest.mark.asyncio
async def test_request_code_fails_when_status_code_is_different_from_401(monkeypatch):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', AsyncMock(return_value=mock_response()))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    with pytest.raises(NuException) as ex:
        email = await generator.request_code()

        assert ex is not None
        assert email is None


@pytest.mark.asyncio
async def test_request_code_fails_when_there_is_no_authenticate_header(monkeypatch):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', AsyncMock(return_value=mock_response(None, {}, 401)))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    with pytest.raises(NuException) as ex:
        email = await generator.request_code()

        assert ex is not None
        assert email is None


@pytest.mark.asyncio
async def test_request_code(monkeypatch):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', AsyncMock(return_value=mock_response(None, headers, 401)))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    email = await generator.request_code()

    assert email == 'john@doe'
    assert generator.encrypted_code == 'abc123'


@pytest.mark.asyncio
async def test_exchange_certs_fails_when_called_without_request_code(monkeypatch):
    http = MockHttpClient()

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    with pytest.raises(NuException) as ex:
        cert1, cert2 = await generator.exchange_certs('1234')

        assert cert1 is None
        assert cert2 is None
        assert ex is not None


@pytest.mark.asyncio
async def test_exchange_cert_fails_when_status_code_is_different_from_200(monkeypatch):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', AsyncMock(return_value=mock_response(None, headers, 401)))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    await generator.request_code()

    with pytest.raises(NuException) as ex:
        cert1, cert2 = await generator.exchange_certs('1234')

        assert cert1 is None
        assert cert2 is None
        assert ex is not None


@pytest.mark.asyncio
async def test_exchange_certs(monkeypatch, gen_certificate_return):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', AsyncMock(return_value=mock_response(None, headers, 401)))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    await generator.request_code()
    monkeypatch.setattr(http, 'raw_post', AsyncMock(return_value=mock_response(gen_certificate_return, headers, 200)))
    cert1, cert2 = await generator.exchange_certs('1234')

    assert cert1 is not None
    assert cert2 is not None
