import pycurl
from io import BytesIO
from pynubank import NuRequestException


class HttpClient:

    def __init__(self):
        self._cert = None
        self._headers = [
            'Content-Type: application/json',
            'X-Correlation-Id: and-7-86-2-1000005524.9twu3pgr',
            'User-Agent: pynubank Client - https://github.com/andreroggeri/pynubank',
        ]

    def set_cert_data(self, cert_data: bytes):
        self._cert = cert_data

    def set_header(self, name: str, value: str):
        self._headers.append(f'{name}: {value}')

    def remove_header(self, name: str):
        self._headers = [h for h in self._headers if not h.startswith(f'{name}:')]

    def get_header(self, name: str):
        for h in self._headers:
            if h.startswith(f'{name}:'):
                return h.split(': ', 1)[1]
        return None

    @property
    def _cert_args(self):
        return {'cert': self._cert, 'key': ''} if self._cert else {}

    def _handle_response(self, response: bytes, http_code: int) -> dict:
        if http_code != 200:
            raise NuRequestException(http_code)

        return response

    def raw_get(self, url: str) -> bytes:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.HTTPHEADER, self._headers)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        http_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        return buffer.getvalue(), http_code

    def raw_post(self, url: str, json: dict) -> bytes:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.HTTPHEADER, self._headers)
        c.setopt(c.POSTFIELDS, json)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        http_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        return buffer.getvalue(), http_code

    def get(self, url: str) -> dict:
        response, http_code = self.raw_get(url)
        return self._handle_response(response, http_code)

    def post(self, url: str, json: dict) -> dict:
        json_data = json.dumps(json)  # Convert dict to JSON string
        response, http_code = self.raw_post(url, json_data)
        return self._handle_response(response, http_code)
