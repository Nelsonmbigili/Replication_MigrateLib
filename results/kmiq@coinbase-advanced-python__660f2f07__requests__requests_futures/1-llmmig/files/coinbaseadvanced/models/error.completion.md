### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. The `requests` library was replaced with `requests_futures` in the import statement.
2. The `requests.Response` type hint in the `not_ok_response` method was updated to `requests_futures.sessions.FuturesSession.Response` because `requests_futures` uses `FuturesSession` for asynchronous requests, and its `Response` object is compatible with `requests`.

No other changes were made to the code, as the functionality and structure remain the same.

### Modified Code:
```python
"""
Encapsulating error types.
"""

import json
from requests_futures.sessions import FuturesSession


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
    def not_ok_response(cls, response: FuturesSession.Response) -> 'CoinbaseAdvancedTradeAPIError':
        """
        Factory Method for Coinbase Advanced errors.
        """

        try:
            error_result = json.loads(response.text)
        except ValueError:
            error_result = {'reason': response.text}

        return cls(error_dict=error_result)
```

### Key Notes:
- The `requests_futures` library is designed for asynchronous HTTP requests, but the provided code does not explicitly use asynchronous features. Therefore, the migration only required updating the import and type hint.
- The `FuturesSession.Response` object is compatible with the `requests.Response` object, so no further changes were necessary.