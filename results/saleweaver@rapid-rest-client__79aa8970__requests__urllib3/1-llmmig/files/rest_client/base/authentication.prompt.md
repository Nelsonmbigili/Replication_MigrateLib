The following Python code currently uses the library "requests" version 2.32.2.
Migrate this code to use the library "urllib3" version 2.4.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "urllib3".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "urllib3".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from requests.auth import AuthBase


class Authentication(AuthBase):
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def __call__(self, r):
        r.headers['Authorization'] = f'{self.type} {self.token}'
        return r


```