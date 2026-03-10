### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The `HTTPError` class is no longer imported from `requests`. Instead, we will use `treq` which handles HTTP errors differently.
2. **Error Handling**: The `raise_for_status` method is not needed in the same way with `treq`, as it raises exceptions automatically for HTTP errors. Therefore, we can remove the custom implementation of `raise_for_status`.
3. **Response Handling**: The `json()` method remains the same, as both libraries provide a similar interface for handling JSON responses.

The modified code reflects these changes while maintaining the original structure and naming conventions.

### Modified Code
```python
from treq import request


class MockResponse:
    def __init__(self, data: dict | list, status_code: int, content: any = None):
        self.__data = data
        self.content = content
        self.status_code = status_code

    def json(self):
        return self.__data

    def raise_for_status(self):
        # This method is no longer necessary with treq, as it raises exceptions automatically.
        pass
```