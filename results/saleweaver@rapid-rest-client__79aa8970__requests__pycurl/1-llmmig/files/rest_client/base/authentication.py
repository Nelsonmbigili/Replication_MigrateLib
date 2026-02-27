import pycurl


class Authentication:
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def apply_auth(self, curl):
        """
        Configures the pycurl object with the Authorization header.
        :param curl: pycurl.Curl object
        """
        auth_header = f'{self.type} {self.token}'
        curl.setopt(pycurl.HTTPHEADER, [f'Authorization: {auth_header}'])
