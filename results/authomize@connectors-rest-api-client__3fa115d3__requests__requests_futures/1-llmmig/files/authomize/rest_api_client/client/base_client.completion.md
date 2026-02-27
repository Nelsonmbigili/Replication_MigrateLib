### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Changes**: Replaced the `requests` import with `requests_futures`.
2. **Session Replacement**: Replaced `requests.Session()` with `requests_futures.sessions.FuturesSession()` to enable asynchronous requests.
3. **Response Handling**: Since `requests_futures` returns a `Future` object instead of a `Response` object directly, the `.result()` method is used to retrieve the actual `Response` object before passing it to the `_handle_response` method.
4. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the existing application.

### Modified Code:
```python
from typing import Optional

from requests_futures.sessions import FuturesSession
from requests import Response

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.session = FuturesSession()
        self.session.headers.update({'Authorization': self.authorization_header})

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response: Response):
        if response.ok:
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
        future = self.session.get(url, params=params)
        response = future.result()  # Retrieve the actual Response object
        return self._handle_response(response)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        future = self.session.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=body,
        )
        response = future.result()  # Retrieve the actual Response object
        return self._handle_response(response)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        future = self.session.patch(
            url,
            headers={'Content-Type': 'application/json'},
            data=body,
        )
        response = future.result()  # Retrieve the actual Response object
        return self._handle_response(response)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        future = self.session.delete(url, params=params)
        response = future.result()  # Retrieve the actual Response object
        return self._handle_response(response)
```

### Key Notes:
- The `FuturesSession` class from `requests_futures` is used to replace the synchronous `requests.Session`.
- The `.result()` method is called on the `Future` object returned by `FuturesSession` methods (`get`, `post`, `patch`, `delete`) to obtain the `Response` object.
- The rest of the code remains unchanged to ensure compatibility with the existing application logic.