### Explanation of Changes:
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Import Replacement**: Removed the `requests` import and replaced it with `urllib3`.
2. **Response Handling**: Replaced `requests.Response` with `urllib3.response.HTTPResponse` in type hints and method arguments.
3. **Response Status Check**: Replaced `response.ok` (from `requests`) with `response.status == 200` (from `urllib3`).
4. **JSON Parsing**: Replaced `response.json()` (from `requests`) with `json.loads(response.data.decode('utf-8'))` (from `urllib3`), as `urllib3` does not have a built-in `.json()` method.
5. **Error Handling**: Adjusted error handling to work with `urllib3`'s response object.

### Modified Code:
```python
"""
Object models for order related endpoints args and response.
"""

import urllib3
import json

from coinbaseadvanced.models.error import CoinbaseAdvancedTradeAPIError


class BaseModel:
    """
    Base class for models.
    """

    def __str__(self):
        attributes = ", ".join(
            f"{key}={value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes})"

    def __repr__(self):
        attributes = ", ".join(
            f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes})"


class EmptyResponse(BaseModel):
    """
    Represents an empty response from the Coinbase Advanced Trade API.

    Attributes:
        success (bool): Indicates whether the response was successful or not.
    """

    success: bool

    def __init__(self, **kwargs) -> None:
        self.success = True
        self.kwargs = kwargs

    @classmethod
    def from_response(cls, response: urllib3.response.HTTPResponse) -> 'EmptyResponse':
        """
        Factory Method that creates an EmptyResponse object from a urllib3.response.HTTPResponse object.

        Args:
            response (urllib3.response.HTTPResponse): The response object returned by the API.

        Returns:
            EmptyResponse: An instance of the EmptyResponse class.

        Raises:
            CoinbaseAdvancedTradeAPIError: If the response is not OK.
        """

        if response.status != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = json.loads(response.data.decode('utf-8'))
        return cls(**result)


class UnixTime(BaseModel):
    """
    Unix time in different formats.
    """

    iso: str
    epochSeconds: str
    epochMillis: str

    def __init__(self,
                 iso: str,
                 epochSeconds: str,
                 epochMillis: str,
                 **kwargs
                 ) -> None:

        self.iso = iso
        self.epochSeconds = epochSeconds
        self.epochMillis = epochMillis

        self.kwargs = kwargs

    @classmethod
    def from_response(cls, response: urllib3.response.HTTPResponse) -> 'UnixTime':
        """
        Factory Method.
        """

        if response.status != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = json.loads(response.data.decode('utf-8'))
        return cls(**result)


class ValueCurrency(BaseModel):
    """
    Available Balance object.
    """

    value: str
    currency: str

    def __init__(self, value: str, currency: str, **kwargs) -> None:
        self.value = value
        self.currency = currency

        self.kwargs = kwargs
```

### Key Notes:
- The `urllib3` library does not have a `.json()` method for parsing JSON responses, so `json.loads()` is used instead.
- The `response.ok` attribute from `requests` is replaced with `response.status == 200` to check for successful responses.
- The `urllib3.response.HTTPResponse` object is used in place of `requests.Response` for type hints and method arguments.
- No other changes were made to the structure, logic, or style of the code to ensure compatibility with the rest of the application.