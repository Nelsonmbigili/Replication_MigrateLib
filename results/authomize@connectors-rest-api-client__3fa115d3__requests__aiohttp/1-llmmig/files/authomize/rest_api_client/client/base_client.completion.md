### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Session Management**: Replaced `requests.Session` with `aiohttp.ClientSession`. The session is now asynchronous and must be used within an `async` context.
2. **HTTP Methods**: Updated `http_get`, `http_post`, `http_patch`, and `http_delete` to use `aiohttp`'s asynchronous methods (`get`, `post`, `patch`, `delete`).
3. **Response Handling**: Updated `_handle_response` and `_handle_ok_response` to work with `aiohttp.ClientResponse`, which requires `await` to access the response body or JSON.
4. **Initialization**: Added an `async` method `initialize_session` to create the `aiohttp.ClientSession` since it must be initialized asynchronously.
5. **Cleanup**: Added an `async` method `close_session` to properly close the `aiohttp.ClientSession`.
6. **Asynchronous Methods**: Made all HTTP methods (`http_get`, `http_post`, `http_patch`, `http_delete`) asynchronous by adding the `async` keyword and using `await` where necessary.

### Modified Code
```python
from typing import Optional

import aiohttp

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.session = None  # aiohttp.ClientSession will be initialized asynchronously

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    async def initialize_session(self):
        """Initialize the aiohttp session asynchronously."""
        self.session = aiohttp.ClientSession(
            headers={'Authorization': self.authorization_header}
        )

    async def close_session(self):
        """Close the aiohttp session asynchronously."""
        if self.session:
            await self.session.close()

    @staticmethod
    async def _handle_response(response: aiohttp.ClientResponse):
        if response.status < 400:
            return await BaseClient._handle_ok_response(response)
        try:
            response_json = await response.json()
            detail = response_json.get('detail')
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        response.raise_for_status()

    @staticmethod
    async def _handle_ok_response(response: aiohttp.ClientResponse) -> dict:
        if content_type := response.headers.get('content-type'):
            if content_type.startswith('application/json'):
                return await response.json()

        raise ClientError(
            message={
                'status_code': response.status,
                'url': str(response.url),
                'message': 'Unexpected response from API',
                'raw': await response.read(),
            },
        )

    async def http_get(self, url, params=None):
        url = self.base_url + url
        async with self.session.get(url, params=params) as response:
            return await self._handle_response(response)

    async def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        async with self.session.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=body,
        ) as response:
            return await self._handle_response(response)

    async def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        async with self.session.patch(
            url,
            headers={'Content-Type': 'application/json'},
            data=body,
        ) as response:
            return await self._handle_response(response)

    async def http_delete(self, url: str, params=None):
        url = self.base_url + url
        async with self.session.delete(url, params=params) as response:
            return await self._handle_response(response)
```

### Key Notes
1. **Session Lifecycle**: The `aiohttp.ClientSession` must be explicitly initialized and closed. This is why `initialize_session` and `close_session` methods were added.
2. **Asynchronous Context**: All HTTP methods (`http_get`, `http_post`, etc.) are now `async` and must be called within an asynchronous context using `await`.
3. **Response Handling**: Accessing the response body or JSON in `aiohttp` requires `await`, which is reflected in `_handle_response` and `_handle_ok_response`.

This migration ensures the code is fully compatible with `aiohttp` while maintaining the original structure and functionality.