import pycurl
import json
from io import BytesIO

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
        return {'pkcs12_data': self._cert, 'pkcs12_password': ''} if self._cert else {}

    def _handle_response(self, response_data: bytes, status_code: int) -> dict:
        if status_code != 200:
            raise NuRequestException(f"HTTP Error: {status_code}, Response: {response_data.decode('utf-8')}")

        return json.loads(response_data.decode('utf-8'))

    def _make_request(self, url: str, method: str, json_data: dict = None) -> (bytes, int):
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)

        # Set headers
        headers = [f"{key}: {value}" for key, value in self._headers.items()]
        curl.setopt(pycurl.HTTPHEADER, headers)

        # Handle certificate if provided
        if self._cert:
            curl.setopt(pycurl.SSLCERTTYPE, "P12")
            curl.setopt(pycurl.SSLCERT, self._cert)
            curl.setopt(pycurl.SSLKEYPASSWD, '')

        # Handle POST method
        if method == "POST":
            curl.setopt(pycurl.POST, 1)
            if json_data:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(json_data))

        # Perform the request
        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            raise NuRequestException(f"Request failed: {e}")
        finally:
            curl.close()

        return buffer.getvalue(), status_code

    def raw_get(self, url: str) -> (bytes, int):
        return self._make_request(url, "GET")

    def raw_post(self, url: str, json: dict) -> (bytes, int):
        return self._make_request(url, "POST", json)

    def get(self, url: str) -> dict:
        response_data, status_code = self.raw_get(url)
        return self._handle_response(response_data, status_code)

    def post(self, url: str, json: dict) -> dict:
        response_data, status_code = self.raw_post(url, json)
        return self._handle_response(response_data, status_code)
