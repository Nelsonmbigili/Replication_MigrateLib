### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Session Management**: The `requests.Session` object was removed, as `pycurl` does not have a direct equivalent. Instead, each HTTP request is handled individually using a `pycurl.Curl` object.
2. **HTTP Methods**: The `http_get`, `http_post`, `http_patch`, and `http_delete` methods were rewritten to use `pycurl` for making HTTP requests. This includes setting the appropriate HTTP method, headers, and data for each request.
3. **Response Handling**: Since `pycurl` does not return a `Response` object like `requests`, the response data is captured using a `BytesIO` buffer. The response headers and body are then parsed manually.
4. **Error Handling**: `pycurl` raises exceptions for connection errors, so these are caught and re-raised as `ClientError` where appropriate.
5. **Headers**: Headers are set explicitly for each request using the `setopt` method of the `pycurl.Curl` object.

### Modified Code:
```python
from typing import Optional
import pycurl
from io import BytesIO
import json

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.default_headers = {'Authorization': self.authorization_header}

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response_body: bytes, response_headers: dict, status_code: int, url: str) -> dict:
        if 200 <= status_code < 300:
            content_type = response_headers.get('content-type', '')
            if content_type.startswith('application/json'):
                return json.loads(response_body.decode('utf-8'))

            raise ClientError(
                message={
                    'status_code': status_code,
                    'url': url,
                    'message': 'Unexpected response from API',
                    'raw': response_body,
                },
            )
        else:
            try:
                response_json = json.loads(response_body.decode('utf-8'))
                detail = response_json.get('detail')
            except Exception:
                detail = None

            if detail:
                raise ClientError(str(detail))
            else:
                raise ClientError(f"HTTP {status_code}: {response_body.decode('utf-8')}")

    def _make_request(self, method: str, url: str, headers: dict, body: Optional[str] = None, params: Optional[dict] = None):
        curl = pycurl.Curl()
        response_body = BytesIO()
        response_headers = BytesIO()

        # Construct the full URL
        if params:
            query_string = '&'.join(f"{key}={value}" for key, value in params.items())
            url = f"{url}?{query_string}"

        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, response_body.write)
        curl.setopt(pycurl.HEADERFUNCTION, response_headers.write)

        # Set HTTP method
        if method == 'POST':
            curl.setopt(pycurl.POST, 1)
        elif method == 'PATCH':
            curl.setopt(pycurl.CUSTOMREQUEST, 'PATCH')
        elif method == 'DELETE':
            curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        elif method == 'GET':
            curl.setopt(pycurl.HTTPGET, 1)

        # Set headers
        all_headers = self.default_headers.copy()
        if headers:
            all_headers.update(headers)
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in all_headers.items()])

        # Set body if provided
        if body:
            curl.setopt(pycurl.POSTFIELDS, body)

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            response_headers_dict = self._parse_headers(response_headers.getvalue().decode('utf-8'))
            return self._handle_response(response_body.getvalue(), response_headers_dict, status_code, url)
        except pycurl.error as e:
            raise ClientError(f"Request failed: {str(e)}")
        finally:
            curl.close()

    @staticmethod
    def _parse_headers(headers: str) -> dict:
        header_lines = headers.splitlines()
        header_dict = {}
        for line in header_lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                header_dict[key.lower()] = value
        return header_dict

    def http_get(self, url, params=None):
        url = self.base_url + url
        return self._make_request('GET', url, headers={}, params=params)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        return self._make_request('POST', url, headers={'Content-Type': 'application/json'}, body=body)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        return self._make_request('PATCH', url, headers={'Content-Type': 'application/json'}, body=body)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        return self._make_request('DELETE', url, headers={}, params=params)
```

### Key Notes:
- The `_make_request` method centralizes the logic for making HTTP requests using `pycurl`.
- The `_parse_headers` method converts raw response headers into a dictionary for easier access.
- The `http_get`, `http_post`, `http_patch`, and `http_delete` methods now call `_make_request` with the appropriate HTTP method and parameters.
- Error handling and response parsing are adjusted to work with `pycurl`.