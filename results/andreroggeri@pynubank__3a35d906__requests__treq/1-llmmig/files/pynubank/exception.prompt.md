The following Python code currently uses the library "requests" version 2.31.0.
Migrate this code to use the library "treq" version 24.9.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "treq".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "treq".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from requests import Response


class NuException(Exception):

    def __init__(self, message):
        super().__init__(message)


class NuInvalidAuthenticationMethod(NuException):
    def __init__(self, message):
        super().__init__(message)


class NuMissingCreditCard(NuException):
    def __init__(self):
        super().__init__(f'Couldn\'t fetch bills due to missing credit card.')


class NuRequestException(NuException):
    def __init__(self, response: Response):
        super().__init__(f'The request made failed with HTTP status code {response.status_code}')
        self.url = response.url
        self.status_code = response.status_code
        self.response = response

```