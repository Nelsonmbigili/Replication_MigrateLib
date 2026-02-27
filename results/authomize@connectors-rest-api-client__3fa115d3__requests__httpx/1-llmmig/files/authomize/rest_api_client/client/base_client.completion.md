### Explanation of Changes
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Session Replacement**: Replaced `requests.Session()` with `httpx.Client()`. The `httpx.Client` is the equivalent of `requests.Session` and allows for connection pooling and persistent headers.
2. **Response Object**: Updated the type hints and references to the `Response` object to use `httpx.Response` instead of `requests.Response`.
3. **Headers Update**: The `httpx.Client` uses the same `headers.update()` method as `requests.Session`, so no changes were needed here.
4. **Request Methods**: Updated the `get`, `post`, `patch`, and `delete` methods to use `httpx.Client` methods. The method signatures and behavior are similar to `requests`.
5. **Response Handling**: The `httpx.Response` object is compatible with most of the operations used in the code (e.g., `.ok`, `.json()`, `.headers`, `.status_code`, `.raise_for_status()`), so minimal changes were required.
6. **Content-Type Check**: The logic for checking the `content-type` header remains unchanged, as `httpx.Response.headers` behaves the same as `requests.Response.headers`.

### Modified Code
Here is the complete code after migrating to `httpx`:

```python
from typing import Optional

import httpx
from httpx import Response

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.session = httpx.Client()
        self.session.headers.update({'Authorization': self.authorization_header})

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response: Response):
        if response.status_code >= 200 and response.status_code < 300:
            return BaseClient._handle_ok_response(response)
        try:
            response_json = response.json()
            detail = response_json.get('detail')
            if 400 <= response.status_code < 500:
                response.reason = response.text
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        response.raise_for_status()

    @staticmethod
    def _handle_ok_response(response: Response) -> dict:
        if content_type := response.headers.get('content-type'):
            if content_type.startswith('application/json'):
                return response.json()

        raise ClientError(
            message={
                'status_code': response.status_code,
                'url': response.url,
                'message': 'Unexpected response from API',
                'raw': response.content,
            },
        )

    def http_get(self, url, params=None):
        url = self.base_url + url
        response = self.session.get(url, params=params)
        return self._handle_response(response)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = self.session.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=body,
        )
        return self._handle_response(response)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = self.session.patch(
            url,
            headers={'Content-Type': 'application/json'},
            data=body,
        )
        return self._handle_response(response)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        response = self.session.delete(url, params=params)
        return self._handle_response(response)
```

### Key Notes
- The migration was straightforward because `httpx` is designed to be a drop-in replacement for `requests` in many cases.
- The `httpx.Client` and `httpx.Response` objects are very similar to their `requests` counterparts, so the changes were minimal.
- The logic for handling responses, headers, and exceptions remains unchanged, as `httpx` provides similar functionality.