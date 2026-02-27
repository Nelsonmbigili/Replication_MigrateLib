### Explanation of Changes:
To migrate the code from using the `requests` library to `aiohttp`, the following changes were made:
1. Replaced the `requests.Response` type hint with `aiohttp.ClientResponse` in the `not_ok_response` method.
2. Updated the `response.text` attribute to use `await response.text()` since `aiohttp` operations are asynchronous.
3. Added `async` to the `not_ok_response` method to handle the asynchronous nature of `aiohttp`.

### Modified Code:
```python
"""
Encapsulating error types.
"""

import json
from aiohttp import ClientResponse


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
    async def not_ok_response(cls, response: ClientResponse) -> 'CoinbaseAdvancedTradeAPIError':
        """
        Factory Method for Coinbase Advanced errors.
        """

        try:
            error_result = json.loads(await response.text())
        except ValueError:
            error_result = {'reason': await response.text()}

        return cls(error_dict=error_result)
```

### Key Points:
- The `not_ok_response` method is now asynchronous (`async def`) to accommodate the asynchronous nature of `aiohttp`.
- The `response.text` attribute from `requests` is replaced with `await response.text()` in `aiohttp` to retrieve the response body.
- The `requests.Response` type hint is replaced with `aiohttp.ClientResponse`.