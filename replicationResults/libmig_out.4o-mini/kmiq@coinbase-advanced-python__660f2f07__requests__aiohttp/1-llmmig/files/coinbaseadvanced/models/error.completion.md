### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `aiohttp`.
2. **Response Handling**: The `requests.Response` object is replaced with `aiohttp.ClientResponse`. The way to access the response content has changed; instead of using `response.text`, we now use `await response.text()` since `aiohttp` is asynchronous.
3. **Asynchronous Context**: The method `not_ok_response` needs to be modified to be asynchronous to accommodate the `await` keyword when fetching the response text.

### Modified Code
```python
"""
Encapsulating error types.
"""

import json
import aiohttp


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
    async def not_ok_response(cls, response: aiohttp.ClientResponse) -> 'CoinbaseAdvancedTradeAPIError':
        """
        Factory Method for Coinbase Advanced errors.
        """

        try:
            error_result = json.loads(await response.text())
        except ValueError:
            error_result = {'reason': await response.text()}

        return cls(error_dict=error_result)
```