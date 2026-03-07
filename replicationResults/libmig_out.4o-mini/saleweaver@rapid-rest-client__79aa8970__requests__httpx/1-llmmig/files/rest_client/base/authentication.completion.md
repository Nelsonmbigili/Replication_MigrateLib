### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. The import statement for `AuthBase` was removed, as `httpx` does not require a separate authentication base class.
2. The method of setting the authorization header remains the same, but the way to handle the request object is slightly different in `httpx`. Instead of modifying the request directly, we will use the `httpx.Request` object.

### Modified Code
```python
class Authentication:
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def __call__(self, request):
        request.headers['Authorization'] = f'{self.type} {self.token}'
        return request
```