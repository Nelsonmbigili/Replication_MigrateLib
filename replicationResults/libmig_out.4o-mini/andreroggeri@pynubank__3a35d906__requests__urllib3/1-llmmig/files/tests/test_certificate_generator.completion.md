### Explanation of Changes

To migrate the code from using the `requests` library to using `urllib3`, the following changes were made:

1. **Response Object**: The `Response` object from `requests` was replaced with a custom response handling using `urllib3`. Since `urllib3` does not have a direct equivalent to `requests.Response`, we will create a simple mock response class to simulate the behavior of the `requests.Response` object.

2. **HTTP Client**: The `MockHttpClient` class is assumed to be a wrapper around the HTTP client. We will need to ensure that it uses `urllib3` for making requests. However, since the implementation of `MockHttpClient` is not provided, we will focus on the response handling.

3. **Content Handling**: The way content is set in the response has been adjusted to fit the `urllib3` style.

Here is the modified code:

```python
import json
from unittest.mock import MagicMock

import pytest
from urllib3 import HTTPResponse

from pynubank import NuException, MockHttpClient
from pynubank.utils.certificate_generator import CertificateGenerator
from pynubank.utils.discovery import Discovery

headers = {
    'WWW-Authenticate': 'device-authorization encrypted-code="abc123", sent-to="john@doe"'
}

class MockHTTPResponse:
    def __init__(self, status_code, headers=None, content=None):
        self.status = status_code
        self.headers = headers or {}
        self.data = json.dumps(content).encode() if content else b''

    def read(self):
        return self.data

def fake_update_proxy(self: Discovery):
    self.proxy_list_app_url = {
        'gen_certificate': 'https://some-url/gen-cert',
    }

def mock_response(content=None, return_headers=None, status_code=200):
    return MockHTTPResponse(status_code, return_headers, content)

def test_request_code_fails_when_status_code_is_different_from_401(monkeypatch):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', MagicMock(return_value=mock_response()))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    with pytest.raises(NuException) as ex:
        email = generator.request_code()

        assert ex is not None
        assert email is None

def test_request_code_fails_when_there_is_no_authenticate_header(monkeypatch):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', MagicMock(return_value=mock_response(None, {}, 401)))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    with pytest.raises(NuException) as ex:
        email = generator.request_code()

        assert ex is not None
        assert email is None

def test_request_code(monkeypatch):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', MagicMock(return_value=mock_response(None, headers, 401)))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    email = generator.request_code()

    assert email == 'john@doe'
    assert generator.encrypted_code == 'abc123'

def test_exchange_certs_fails_when_called_without_request_code(monkeypatch):
    http = MockHttpClient()

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    with pytest.raises(NuException) as ex:
        cert1, cert2 = generator.exchange_certs('1234')

        assert cert1 is None
        assert cert2 is None
        assert ex is not None

def test_exchange_cert_fails_when_status_code_is_different_from_200(monkeypatch):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', MagicMock(return_value=mock_response(None, headers, 401)))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    generator.request_code()

    with pytest.raises(NuException) as ex:
        cert1, cert2 = generator.exchange_certs('1234')

        assert cert1 is None
        assert cert2 is None
        assert ex is not None

def test_exchange_certs(monkeypatch, gen_certificate_return):
    http = MockHttpClient()
    monkeypatch.setattr(http, 'raw_post', MagicMock(return_value=mock_response(None, headers, 401)))

    generator = CertificateGenerator('123456789', 'hunter12', '1234', http_client=http)

    generator.request_code()
    monkeypatch.setattr(http, 'raw_post', MagicMock(return_value=mock_response(gen_certificate_return, headers, 200)))
    cert1, cert2 = generator.exchange_certs('1234')

    assert cert1 is not None
    assert cert2 is not None
```

This code now uses `urllib3` for HTTP responses while maintaining the original structure and logic of the code.