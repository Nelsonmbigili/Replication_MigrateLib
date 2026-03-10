### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Importing the FutureSession**: Instead of using `requests.Session()`, we now use `requests_futures.sessions.FutureSession()`. This allows us to make asynchronous requests.
  
2. **Making Asynchronous Requests**: The methods that perform HTTP requests (`http_get`, `http_post`, `http_patch`, and `http_delete`) now use the `session.get()`, `session.post()`, `session.patch()`, and `session.delete()` methods, which return a `Future` object. We need to call `.result()` on this `Future` object to get the actual `Response` object.

3. **Handling the Response**: The response handling remains the same, but we now need to ensure that we call `.result()` on the future to get the response before passing it to `_handle_response`.

Here is the modified code:

```python
from typing import Optional

import requests_futures
from requests_futures.sessions import FutureSession
from requests import Response

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.session = FutureSession()
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
        response = future.result()  # Get the actual Response object
        return self._handle_response(response)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        future = self.session.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=body,
        )
        response = future.result()  # Get the actual Response object
        return self._handle_response(response)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        future = self.session.patch(
            url,
            headers={'Content-Type': 'application/json'},
            data=body,
        )
        response = future.result()  # Get the actual Response object
        return self._handle_response(response)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        future = self.session.delete(url, params=params)
        response = future.result()  # Get the actual Response object
        return self._handle_response(response)
``` 

This code now uses `requests_futures` to handle HTTP requests asynchronously while maintaining the original structure and functionality.