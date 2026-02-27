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
