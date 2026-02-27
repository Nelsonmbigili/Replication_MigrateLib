### Explanation of Changes:
The original code uses the `requests` library's `AuthBase` class to implement custom authentication by modifying the `Authorization` header. Since `pycurl` does not have a direct equivalent to `AuthBase`, the migration involves manually setting the `Authorization` header using `pycurl`'s options. The `BearerTokenAuth` class is modified to store the token and type, and a new method is added to configure the `pycurl` object with the appropriate header.

### Modified Code:
```python
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
```

### Key Changes:
1. **Removed `AuthBase` Inheritance**: Since `pycurl` does not have an equivalent to `AuthBase`, the `Authentication` class is now a simple base class.
2. **Replaced `__call__` Method**: The `__call__` method, which modifies the `requests` request object, is replaced with an `apply_auth` method. This method configures the `pycurl.Curl` object by setting the `Authorization` header using `pycurl.HTTPHEADER`.
3. **Header Configuration**: The `Authorization` header is set using `pycurl.HTTPHEADER`, which accepts a list of headers.

This modified code is now compatible with `pycurl` and can be used to set the `Authorization` header for HTTP requests.