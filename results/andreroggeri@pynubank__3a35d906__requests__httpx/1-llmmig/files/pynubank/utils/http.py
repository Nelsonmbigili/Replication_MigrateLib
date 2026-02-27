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
