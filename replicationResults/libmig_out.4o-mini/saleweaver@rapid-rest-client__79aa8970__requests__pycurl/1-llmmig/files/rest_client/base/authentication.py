import pycurl
from io import BytesIO


class Authentication:
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def __call__(self, url):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.HTTPHEADER, [f'Authorization: {self.type} {self.token}'])
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        return buffer.getvalue()
