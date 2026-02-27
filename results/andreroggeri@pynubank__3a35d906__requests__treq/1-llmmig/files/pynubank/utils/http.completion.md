### Explanation of Changes:
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Replaced `requests` and `requests_pkcs12` with `treq`**:
   - `treq` is an asynchronous HTTP client, so the methods `raw_get`, `raw_post`, `get`, and `post` were updated to be asynchronous.
   - The `treq` library does not natively support PKCS#12 certificates. Instead, the `pyOpenSSL` library is used to load the certificate, and the resulting `SSLContext` is passed to `treq` for secure connections.
2. **Updated `_cert_args`**:
   - The `_cert_args` property now creates an `SSLContext` using `pyOpenSSL` to handle the PKCS#12 certificate.
3. **Modified `_handle_response`**:
   - Since `treq` returns a `Deferred` object, the response handling is now asynchronous. The `json()` method of `treq` is used to parse the response body.
4. **Updated `raw_get` and `raw_post`**:
   - These methods now use `treq.get` and `treq.post`, which are asynchronous.
5. **Updated `get` and `post`**:
   - These methods are now asynchronous and await the results of `raw_get` and `raw_post`.

### Modified Code:
```python
import treq
from OpenSSL import crypto
from twisted.internet.ssl import CertificateOptions
from twisted.internet.defer import ensureDeferred

from pynubank import NuRequestException


class HttpClient:

    def __init__(self):
        self._cert = None
        self._headers = {
            'Content-Type': 'application/json',
            'X-Correlation-Id': 'and-7-86-2-1000005524.9twu3pgr',
            'User-Agent': 'pynubank Client - https://github.com/andreroggeri/pynubank',
        }

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

        # Load the PKCS#12 certificate
        pkcs12 = crypto.load_pkcs12(self._cert, b'')
        private_key = pkcs12.get_privatekey()
        certificate = pkcs12.get_certificate()
        additional_certs = pkcs12.get_ca_certificates() or []

        # Create an SSLContext using the certificate and private key
        context = CertificateOptions(
            privateKey=crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key),
            certificate=crypto.dump_certificate(crypto.FILETYPE_PEM, certificate),
            extraCertChain=[
                crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
                for cert in additional_certs
            ]
        )
        return {'context': context}

    async def _handle_response(self, response) -> dict:
        if response.code != 200:
            body = await response.text()
            raise NuRequestException(f"HTTP {response.code}: {body}")

        return await response.json()

    async def raw_get(self, url: str):
        return await treq.get(url, headers=self._headers, **self._cert_args)

    async def raw_post(self, url: str, json: dict):
        return await treq.post(url, json=json, headers=self._headers, **self._cert_args)

    async def get(self, url: str) -> dict:
        response = await self.raw_get(url)
        return await self._handle_response(response)

    async def post(self, url: str, json: dict) -> dict:
        response = await self.raw_post(url, json)
        return await self._handle_response(response)
```

### Key Notes:
1. **Asynchronous Nature**:
   - Since `treq` is asynchronous, all methods that interact with it (`raw_get`, `raw_post`, `get`, `post`, and `_handle_response`) are now `async def` and must be awaited.
   - If this class is used in a synchronous context, you will need to use `twisted.internet.defer.ensureDeferred` or similar mechanisms to bridge the gap.
2. **Certificate Handling**:
   - The `requests_pkcs12` library simplifies PKCS#12 certificate handling, but `treq` requires manual handling using `pyOpenSSL` to create an `SSLContext`.
3. **Error Handling**:
   - The `NuRequestException` now includes the HTTP status code and response body for better debugging.

This code assumes that the rest of the application is compatible with asynchronous programming. If not, additional changes may be required to integrate this code.