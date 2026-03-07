class Authentication:
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def __call__(self, request):
        request.headers['Authorization'] = f'{self.type} {self.token}'
        return request
