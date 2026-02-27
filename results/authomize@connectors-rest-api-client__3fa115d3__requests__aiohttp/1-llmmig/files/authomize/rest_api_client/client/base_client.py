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
