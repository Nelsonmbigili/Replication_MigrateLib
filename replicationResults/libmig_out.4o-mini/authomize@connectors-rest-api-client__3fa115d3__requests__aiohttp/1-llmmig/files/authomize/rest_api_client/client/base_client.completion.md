### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp`, which is designed for asynchronous HTTP requests.
2. **Session Management**: Instead of using `requests.Session()`, we create an `aiohttp.ClientSession()` for making requests.
3. **Asynchronous Methods**: The methods that perform HTTP requests (`http_get`, `http_post`, `http_patch`, `http_delete`) were modified to be asynchronous. This requires the use of the `async` keyword and the `await` keyword when calling the session methods.
4. **Response Handling**: The response handling logic remains largely the same, but we now await the response and use `await response.json()` to parse JSON data.
5. **Error Handling**: The error handling logic was adjusted to work with the asynchronous nature of `aiohttp`.

Here is the modified code:

```python
from typing import Optional
import aiohttp
import asyncio

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
        self.session.headers.update({'Authorization': self.authorization_header})

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    async def _handle_response(response):
        if response.status == 200:
            return await BaseClient._handle_ok_response(response)
        try:
            response_json = await response.json()
            detail = response_json.get('detail')
            if 400 <= response.status < 500:
                response.reason = await response.text()
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        response.raise_for_status()

    @staticmethod
    async def _handle_ok_response(response) -> dict:
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

    async def close(self):
        await self.session.close()
```

### Additional Notes
- The `close` method was added to allow for proper cleanup of the `aiohttp.ClientSession`.
- The methods are now asynchronous, so they should be called within an `async` function or using an event loop.