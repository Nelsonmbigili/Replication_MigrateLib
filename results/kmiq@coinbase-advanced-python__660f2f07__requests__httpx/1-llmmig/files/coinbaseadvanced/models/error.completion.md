### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. Replaced the `requests` import with `httpx`.
2. Updated the type hint for the `response` parameter in the `not_ok_response` method from `requests.Response` to `httpx.Response`, as the `Response` object is specific to each library.
3. No other changes were necessary since the `httpx.Response` object has a `text` attribute similar to `requests.Response`.

### Modified Code
Here is the updated code after migrating to `httpx`:

```python
"""
Encapsulating error types.
"""

import json
import httpx


class CoinbaseAdvancedTradeAPIError(Exception):
    """
    Class CoinbaseAdvancedTradeAPIError is derived from super class Exception
    and represent the default generic error when endpoint request fail.
    """

    def __init__(self, error_dict: dict):
        self.error_dict = error_dict

    def __str__(self):
        return str(self.error_dict)

    @classmethod
    def not_ok_response(cls, response: httpx.Response) -> 'CoinbaseAdvancedTradeAPIError':
        """
        Factory Method for Coinbase Advanced errors.
        """

        try:
            error_result = json.loads(response.text)
        except ValueError:
            error_result = {'reason': response.text}

        return cls(error_dict=error_result)
```

### Summary of Changes
- Replaced `requests` with `httpx` in the import statement.
- Updated the type hint for the `response` parameter in the `not_ok_response` method to use `httpx.Response`.