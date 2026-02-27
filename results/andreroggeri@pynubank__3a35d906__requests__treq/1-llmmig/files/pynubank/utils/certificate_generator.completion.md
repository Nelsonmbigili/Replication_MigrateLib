### Explanation of Changes
The migration from `requests` to `treq` involves the following changes:
1. **Asynchronous Nature of `treq`**: Unlike `requests`, `treq` is asynchronous. This means that all HTTP calls (`raw_post`) need to be awaited, and the methods containing these calls must be converted to asynchronous methods.
2. **Response Handling**: `treq` provides methods like `response.text()`, `response.json()`, and `response.status` for handling responses. These methods are asynchronous and need to be awaited.
3. **Headers and Status Code**: Accessing headers and status codes in `treq` is slightly different. Headers are accessed using `response.headers.getRawHeaders()` (which returns a list), and the status code is accessed using `response.code`.
4. **Initialization of `HttpClient`**: The `HttpClient` class must be updated to use `treq` for making HTTP requests.

Below is the modified code with the necessary changes.

---

### Modified Code
```python
from typing import Optional

import OpenSSL
from OpenSSL.crypto import X509

from pynubank import NuException, NuRequestException
from pynubank.utils.discovery import Discovery
from pynubank.utils.http import HttpClient


class CertificateGenerator:

    def __init__(self, login, password, device_id, encrypted_code=None, http_client: Optional[HttpClient] = None):
        self.login = login
        self.password = password
        self.device_id = device_id
        self.encrypted_code = encrypted_code
        self.key1 = self._generate_key()
        self.key2 = self._generate_key()
        self.http = HttpClient() if http_client is None else http_client
        discovery = Discovery(self.http)
        self.url = discovery.get_app_url('gen_certificate')

    async def request_code(self) -> str:
        response = await self.http.raw_post(self.url, json=self._get_payload())

        if response.code != 401 or not response.headers.getRawHeaders('WWW-Authenticate'):
            raise NuException('Authentication code request failed.')

        auth_header = response.headers.getRawHeaders('WWW-Authenticate')[0]
        parsed = self._parse_authenticate_headers(auth_header)
        self.encrypted_code = parsed.get('device-authorization_encrypted-code')

        return parsed.get('sent-to')

    async def exchange_certs(self, code: str):
        if not self.encrypted_code:
            raise NuException('No encrypted code found. Did you call `request_code` before exchanging certs ?')

        payload = self._get_payload()
        payload['code'] = code
        payload['encrypted-code'] = self.encrypted_code

        response = await self.http.raw_post(self.url, json=payload)

        if response.code != 200:
            raise NuRequestException(response)

        data = await response.json()

        cert1 = self._parse_cert(data['certificate'])
        cert2 = self._parse_cert(data['certificate_crypto'])

        return self._gen_cert(self.key1, cert1), self._gen_cert(self.key2, cert2)

    def _get_payload(self):
        return {
            'login': self.login,
            'password': self.password,
            'public_key': self._get_public_key(self.key1),
            'public_key_crypto': self._get_public_key(self.key2),
            'model': f'PyNubank Client ({self.device_id})',
            'device_id': self.device_id
        }

    def _parse_cert(self, content: str) -> X509:
        return OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, content.encode())

    def _gen_cert(self, key, cert):
        p12 = OpenSSL.crypto.PKCS12()
        p12.set_privatekey(key)
        p12.set_certificate(cert)

        return p12

    def _generate_key(self):
        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

        return key

    def _get_public_key(self, key) -> str:
        return OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, key).decode()

    def _parse_authenticate_headers(self, header_content: str) -> dict:
        chunks = header_content.split(',')
        parsed = {}
        for chunk in chunks:
            key, value = chunk.split('=')
            key = key.strip().replace(' ', '_')
            value = value.replace('"', '')
            parsed[key] = value

        return parsed
```

---

### Key Changes in the Code
1. **`request_code` and `exchange_certs`**:
   - These methods are now asynchronous (`async def`).
   - The `raw_post` method is awaited (`await self.http.raw_post(...)`).
   - Response handling uses `response.code` for status codes and `response.headers.getRawHeaders()` for headers.

2. **Response Parsing**:
   - `response.json()` is awaited to parse JSON data.
   - `response.headers.getRawHeaders()` is used to fetch headers (returns a list, so the first element is accessed).

3. **No Changes to Non-HTTP Logic**:
   - The rest of the code (e.g., certificate generation, key handling) remains unchanged, as it is unrelated to the HTTP library.

This ensures the code is fully migrated to `treq` while maintaining its original functionality and structure.