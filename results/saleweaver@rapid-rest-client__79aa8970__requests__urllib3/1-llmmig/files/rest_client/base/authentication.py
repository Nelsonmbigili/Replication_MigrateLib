class Authentication:
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def add_auth_header(self, headers):
        """Adds the Authorization header to the provided headers dictionary."""
        headers['Authorization'] = f'{self.type} {self.token}'
        return headers
