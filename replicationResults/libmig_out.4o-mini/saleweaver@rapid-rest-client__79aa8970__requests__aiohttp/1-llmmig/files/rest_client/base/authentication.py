from aiohttp import ClientSession, ClientTimeout
from aiohttp.helpers import BasicAuth


class Authentication:
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    async def __call__(self, session: ClientSession, url: str, **kwargs):
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'{self.type} {self.token}'
        kwargs['headers'] = headers
        async with session.get(url, **kwargs) as response:
            return await response.text()
