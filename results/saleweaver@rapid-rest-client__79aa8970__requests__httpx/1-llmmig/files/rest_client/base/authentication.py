from httpx import Auth


class Authentication(Auth):
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def auth_flow(self, request):
        request.headers['Authorization'] = f'{self.type} {self.token}'
        yield request
