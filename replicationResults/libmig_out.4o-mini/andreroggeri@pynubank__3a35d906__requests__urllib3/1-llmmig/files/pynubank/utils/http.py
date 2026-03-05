from urllib3 import PoolManager
from urllib3.exceptions import HTTPError
from requests_pkcs12 import get, post

from pynubank import NuRequestException


class HttpClient:

    def __init__(self):
        self._cert = None
        self._headers = {
            'Content-Type': 'application/json',
            'X-Correlation-Id': 'and-7-86-2-1000005524.9twu3pgr',
            'User-Agent': 'pynubank Client - https://github.com/andreroggeri/pynubank',
        }
        self.http = PoolManager()

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
        return {'pkcs12_data': self._cert, 'pkcs12_password': ''} if self._cert else {}

    def _handle_response(self, response) -> dict:
        if response.status != 200:
            raise NuRequestException(response)

        return response.data

    def raw_get(self, url: str):
        return self.http.request('GET', url, headers=self._headers, **self._cert_args)

    def raw_post(self, url: str, json: dict):
        return self.http.request('POST', url, headers=self._headers, body=json)

    def get(self, url: str) -> dict:
        return self._handle_response(self.raw_get(url))

    def post(self, url: str, json: dict) -> dict:
        return self._handle_response(self.raw_post(url, json=json))
