class Authentication:
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    async def add_auth_header(self, session, url, **kwargs):
        """
        This method adds the Authorization header to the request.
        It should be called before making a request with aiohttp.
        """
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'{self.type} {self.token}'
        kwargs['headers'] = headers
        async with session.get(url, **kwargs) as response:
            return await response.text()
