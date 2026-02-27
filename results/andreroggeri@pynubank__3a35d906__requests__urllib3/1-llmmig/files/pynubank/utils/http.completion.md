### Explanation of Changes:
The original code uses the `requests` library along with the `requests_pkcs12` extension to handle HTTP requests with PKCS#12 certificates. To migrate to `urllib3`, the following changes were made:
1. Replaced `requests` and `requests_pkcs12` imports with `urllib3`.
2. Used `urllib3.PoolManager` to manage HTTP connections.
3. Replaced `get` and `post` methods from `requests_pkcs12` with `urllib3`'s `request` method.
4. Handled PKCS#12 certificates using `ssl` from Python's standard library, as `urllib3` does not natively support PKCS#12. The certificate is loaded into an `SSLContext` object.
5. Updated the `_cert_args` property to return an `SSLContext` object instead of `requests_pkcs12`-specific arguments.
6. Modified the `_handle_response` method to work with `urllib3`'s `HTTPResponse` object instead of `requests.Response`.

### Modified Code:
```python
import ssl
import json
from urllib3 import PoolManager, HTTPResponse

from pynubank import NuRequestException


class HttpClient:

    def __init__(self):
        self._cert = None
        self._headers = {
            'Content-Type': 'application/json',
            'X-Correlation-Id': 'and-7-86-2-1000005524.9twu3pgr',
            'User-Agent': 'pynubank Client - https://github.com/andreroggeri/pynubank',
        }
        self._http = PoolManager()

    def set_cert_data(self, cert_data: bytes):
        self._cert = cert_data

    def set_header(self, name: str, value: str):
        self._headers[name] = value

    def remove_header(self, name: str):
        self._headers.pop(name)

    def get_header(self, name: str):
        return self._headers.get(name)

    @property
    def _cert_args(self):
        if not self._cert:
            return {}
        # Create an SSLContext for PKCS#12 certificates
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_pkcs12(self._cert, password="")
        return {'ssl_context': ssl_context}

    def _handle_response(self, response: HTTPResponse) -> dict:
        if response.status != 200:
            raise NuRequestException(response)

        return json.loads(response.data.decode('utf-8'))

    def raw_get(self, url: str) -> HTTPResponse:
        return self._http.request(
            'GET',
            url,
            headers=self._headers,
            **self._cert_args
        )

    def raw_post(self, url: str, json: dict) -> HTTPResponse:
        return self._http.request(
            'POST',
            url,
            body=json.dumps(json),
            headers=self._headers,
            **self._cert_args
        )

    def get(self, url: str) -> dict:
        return self._handle_response(self.raw_get(url))

    def post(self, url: str, json: dict) -> dict:
        return self._handle_response(self.raw_post(url, json))
```

### Key Notes:
1. **SSLContext for PKCS#12**: Since `urllib3` does not natively support PKCS#12 certificates, the `ssl` module is used to create an `SSLContext` object, which is passed to `urllib3`'s `PoolManager`.
2. **HTTPResponse Handling**: `urllib3`'s `HTTPResponse` object is used instead of `requests.Response`. The `data` attribute of `HTTPResponse` contains the raw response body, which is decoded and parsed as JSON.
3. **Body Encoding**: For POST requests, the `body` parameter in `urllib3` requires a string, so the JSON payload is serialized using `json.dumps`.

This code maintains the original structure and functionality while replacing `requests` with `urllib3`.