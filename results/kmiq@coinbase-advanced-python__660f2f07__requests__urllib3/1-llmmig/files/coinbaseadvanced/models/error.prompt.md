The following Python code currently uses the library "requests" version 2.32.0.
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
"""
Encapsulating error types.
"""

import json
import requests


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
    def not_ok_response(cls, response: requests.Response) -> 'CoinbaseAdvancedTradeAPIError':
        """
        Factory Method for Coinbase Advanced errors.
        """

        try:
            error_result = json.loads(response.text)
        except ValueError:
            error_result = {'reason': response.text}

        return cls(error_dict=error_result)

```