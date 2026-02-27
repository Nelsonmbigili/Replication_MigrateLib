from typing import Optional
import treq
from twisted.internet.defer import ensureDeferred

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.headers = {'Authorization': self.authorization_header}

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    async def _handle_response(response):
        if response.code < 400:
            return await BaseClient._handle_ok_response(response)
        try:
            response_json = await response.json()
            detail = response_json.get('detail')
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        raise ClientError(f"HTTP {response.code}: {await response.text()}")

    @staticmethod
    async def _handle_ok_response(response) -> dict:
        content_type = response.headers.getRawHeaders('content-type', [None])[0]
        if content_type and content_type.startswith('application/json'):
            return await response.json()

        raise ClientError(
            message={
                'status_code': response.code,
                'url': response.request.absoluteURI.decode(),
                'message': 'Unexpected response from API',
                'raw': await response.content(),
            },
        )

    async def http_get(self, url, params=None):
        url = self.base_url + url
        response = await treq.get(url, headers=self.headers, params=params)
        return await self._handle_response(response)

    async def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = await treq.post(
            url,
            headers={**self.headers, 'Content-Type': 'application/json'},
            data=body,
        )
        return await self._handle_response(response)

    async def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = await treq.patch(
            url,
            headers={**self.headers, 'Content-Type': 'application/json'},
            data=body,
        )
        return await self._handle_response(response)

    async def http_delete(self, url: str, params=None):
        url = self.base_url + url
        response = await treq.delete(url, headers=self.headers, params=params)
        return await self._handle_response(response)
