### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several key changes were made:

1. **Importing PycURL**: The `requests` library was replaced with `pycurl`. The `requests` session management and methods (like `get`, `post`, `patch`, and `delete`) were replaced with equivalent `pycurl` functionality.

2. **Handling HTTP Requests**: The `http_get`, `http_post`, `http_patch`, and `http_delete` methods were modified to use `pycurl` for making HTTP requests. This involved setting up a `pycurl.Curl` object, configuring it with the appropriate options, and handling the response manually.

3. **Response Handling**: Since `pycurl` does not return a response object like `requests`, the response data is captured using a `BytesIO` object. The response headers and body are processed manually.

4. **Error Handling**: The error handling logic was adapted to work with the response data obtained from `pycurl`.

Here is the modified code:

```python
from typing import Optional
import pycurl
from io import BytesIO

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response_body: bytes, response_code: int, response_headers: dict):
        if response_code >= 200 and response_code < 300:
            return BaseClient._handle_ok_response(response_body, response_headers)
        try:
            response_json = json.loads(response_body)
            detail = response_json.get('detail')
            if 400 <= response_code < 500:
                raise ClientError(str(response_body.decode()))
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        raise ClientError(f"HTTP Error: {response_code}")

    @staticmethod
    def _handle_ok_response(response_body: bytes, response_headers: dict) -> dict:
        if 'content-type' in response_headers:
            if response_headers['content-type'].startswith('application/json'):
                return json.loads(response_body)

        raise ClientError(
            message={
                'status_code': response_headers.get('status_code', 500),
                'url': response_headers.get('url', ''),
                'message': 'Unexpected response from API',
                'raw': response_body,
            },
        )

    def http_get(self, url, params=None):
        url = self.base_url + url
        if params:
            url += '?' + '&'.join(f"{key}={value}" for key, value in params.items())
        
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f'Authorization: {self.authorization_header}'])
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_headers = c.getinfo(c.HEADER_SIZE)
        c.close()
        
        response_body = buffer.getvalue()
        return self._handle_response(response_body, response_code, response_headers)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDS, body)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json', f'Authorization: {self.authorization_header}'])
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_headers = c.getinfo(c.HEADER_SIZE)
        c.close()
        
        response_body = buffer.getvalue()
        return self._handle_response(response_body, response_code, response_headers)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.CUSTOMREQUEST, 'PATCH')
        c.setopt(c.POSTFIELDS, body)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json', f'Authorization: {self.authorization_header}'])
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_headers = c.getinfo(c.HEADER_SIZE)
        c.close()
        
        response_body = buffer.getvalue()
        return self._handle_response(response_body, response_code, response_headers)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        if params:
            url += '?' + '&'.join(f"{key}={value}" for key, value in params.items())
        
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.CUSTOMREQUEST, 'DELETE')
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f'Authorization: {self.authorization_header}'])
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        response_headers = c.getinfo(c.HEADER_SIZE)
        c.close()
        
        response_body = buffer.getvalue()
        return self._handle_response(response_body, response_code, response_headers)
```

This code now uses `pycurl` for HTTP requests while maintaining the original structure and functionality of the `BaseClient` class.