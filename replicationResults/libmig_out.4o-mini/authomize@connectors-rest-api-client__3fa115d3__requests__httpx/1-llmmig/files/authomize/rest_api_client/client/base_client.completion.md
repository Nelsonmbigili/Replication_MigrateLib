### Explanation of Changes
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Session Management**: The `httpx` library does not require a session object for making requests. Instead, requests can be made directly using the `httpx` methods.
3. **Response Handling**: The `Response` type from `httpx` is used instead of `requests.Response`. The methods for handling responses remain similar, but they are now called on `httpx` response objects.
4. **Request Methods**: The methods for making GET, POST, PATCH, and DELETE requests were updated to use `httpx` methods directly.

Here is the modified code:

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
        # Removed session as httpx does not require it
        # self.session = requests.Session()
        # self.session.headers.update({'Authorization': self.authorization_header})

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response: Response):
        if response.is_success:  # Changed from response.ok to response.is_success
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
        response = httpx.get(url, params=params, headers={'Authorization': self.authorization_header})  # Added headers
        return self._handle_response(response)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = httpx.post(
            url,
            headers={'Content-Type': 'application/json', 'Authorization': self.authorization_header},  # Added headers
            data=body,
        )
        return self._handle_response(response)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = httpx.patch(
            url,
            headers={'Content-Type': 'application/json', 'Authorization': self.authorization_header},  # Added headers
            data=body,
        )
        return self._handle_response(response)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        response = httpx.delete(url, params=params, headers={'Authorization': self.authorization_header})  # Added headers
        return self._handle_response(response)
``` 

This code now uses the `httpx` library while maintaining the original structure and functionality of the code.