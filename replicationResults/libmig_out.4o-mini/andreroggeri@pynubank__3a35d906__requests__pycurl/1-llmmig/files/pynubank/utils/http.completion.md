### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several changes were necessary:

1. **Import Statements**: The `requests` and `requests_pkcs12` imports were replaced with `pycurl`.
2. **Response Handling**: The `Response` object from `requests` does not exist in `pycurl`. Instead, we need to handle the response manually by using a callback function to capture the response data.
3. **GET and POST Methods**: The `get` and `post` methods were modified to use `pycurl`'s methods for making HTTP requests. This includes setting options for the request and handling the response differently.
4. **Error Handling**: The error handling was adjusted to check for HTTP response codes using `pycurl`'s error handling mechanisms.

Here is the modified code:

```python
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
```

### Key Changes in the Code:
- The `requests` library is replaced with `pycurl`.
- The response handling is done using a `BytesIO` buffer to capture the response data.
- The `raw_get` and `raw_post` methods now return a tuple containing the response data and the HTTP status code.
- The `post` method converts the dictionary to a JSON string before sending it in the request.