### Explanation of Changes
To migrate the code from using the `requests` library to `httpx`, the following changes were made:
1. **Library Import Changes**:
   - Replaced `requests` and `requests_pkcs12` imports with `httpx`.
   - `httpx` natively supports client certificates, so `requests_pkcs12` is no longer needed.

2. **Certificate Handling**:
   - `httpx` uses the `cert` parameter for client certificates. Since `httpx` does not directly support PKCS#12 certificates, you need to convert the PKCS#12 data into a PEM format (certificate and private key) before using it. This requires additional handling, which is implemented in the `_cert_args` property.

3. **Response Handling**:
   - Changed the type of the `response` parameter in `_handle_response` from `requests.Response` to `httpx.Response`.

4. **HTTP Methods**:
   - Replaced `requests.get` and `requests.post` with `httpx.get` and `httpx.post`.

5. **Certificate Argument**:
   - Updated `_cert_args` to handle the PEM certificate and key files required by `httpx`.

### Modified Code
```python
import httpx
from OpenSSL.crypto import load_pkcs12, FILETYPE_PEM
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

        # Convert PKCS#12 data to PEM format
        pkcs12 = load_pkcs12(self._cert, b'')  # Empty password
        cert = pkcs12.get_certificate().to_cryptography().public_bytes(FILETYPE_PEM)
        key = pkcs12.get_privatekey().to_cryptography_key().private_bytes(
            encoding=FILETYPE_PEM,
            format=httpx.PKCS8,
            encryption_algorithm=httpx.NoEncryption()
        )

        return {'cert': (cert, key)}

    def _handle_response(self, response: httpx.Response) -> dict:
        if response.status_code != 200:
            raise NuRequestException(response)

        return response.json()

    def raw_get(self, url: str) -> httpx.Response:
        return httpx.get(url, headers=self._headers, **self._cert_args)

    def raw_post(self, url: str, json: dict) -> httpx.Response:
        return httpx.post(url, json=json, headers=self._headers, **self._cert_args)

    def get(self, url: str) -> dict:
        return self._handle_response(self.raw_get(url))

    def post(self, url: str, json: dict) -> dict:
        return self._handle_response(self.raw_post(url, json=json))
```

### Key Notes:
1. **PKCS#12 Conversion**:
   - `httpx` does not natively support PKCS#12 certificates. The `_cert_args` property converts the PKCS#12 data into PEM format (certificate and private key) using the `OpenSSL` library.

2. **Dependencies**:
   - The `OpenSSL` library is required for handling PKCS#12 certificates. You can install it using `pip install pyopenssl`.

3. **Certificate Password**:
   - The code assumes an empty password for the PKCS#12 certificate. If a password is required, it should be passed to the `load_pkcs12` function.

4. **PEM Format**:
   - The PEM certificate and key are passed as a tuple to the `cert` parameter in `httpx`.

This migration ensures that the functionality remains consistent while using `httpx` instead of `requests`.