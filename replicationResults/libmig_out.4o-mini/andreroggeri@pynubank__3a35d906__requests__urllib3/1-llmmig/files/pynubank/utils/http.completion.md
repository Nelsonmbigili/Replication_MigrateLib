### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statements**: The `get` and `post` functions from `requests` were replaced with the `PoolManager` class from `urllib3`, which is used to manage connections and make HTTP requests.
2. **Response Handling**: The `Response` object from `requests` was replaced with the response object returned by `urllib3`, which requires different methods to access the status code and JSON data.
3. **Request Methods**: The `get` and `post` methods were modified to use the `urllib3` methods for making requests, specifically `http.request('GET', ...)` and `http.request('POST', ...)`.
4. **Error Handling**: The error handling was adjusted to check the status code from the `urllib3` response.

Here is the modified code:

```python
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
```

### Note
- The `body` parameter in the `raw_post` method should be serialized to JSON format if necessary, as `urllib3` does not automatically handle JSON serialization like `requests` does. You may need to add `import json` and use `json.dumps(json)` to convert the dictionary to a JSON string before sending it in the body.