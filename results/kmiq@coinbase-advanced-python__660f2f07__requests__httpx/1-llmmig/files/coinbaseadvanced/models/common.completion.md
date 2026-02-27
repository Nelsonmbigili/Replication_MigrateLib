### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `httpx`.
2. **Response Object**: Updated the type hints and references from `requests.Response` to `httpx.Response` in the `from_response` methods of the `EmptyResponse` and `UnixTime` classes.
3. **Behavioral Consistency**: The `httpx.Response` object is similar to `requests.Response` in terms of attributes like `.ok` and `.json()`, so no further changes were required in the logic.

### Modified Code
Here is the updated code after migrating to `httpx`:

```python
"""
Object models for order related endpoints args and response.
"""

import httpx

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
    def from_response(cls, response: httpx.Response) -> 'EmptyResponse':
        """
        Factory Method that creates an EmptyResponse object from a httpx.Response object.

        Args:
            response (httpx.Response): The response object returned by the API.

        Returns:
            EmptyResponse: An instance of the EmptyResponse class.

        Raises:
            CoinbaseAdvancedTradeAPIError: If the response is not OK.
        """

        if not response.ok:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = response.json()
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
    def from_response(cls, response: httpx.Response) -> 'UnixTime':
        """
        Factory Method.
        """

        if not response.ok:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = response.json()
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

### Summary of Changes
- Replaced `requests` with `httpx` in the import statement.
- Updated type hints and references from `requests.Response` to `httpx.Response` in the `from_response` methods.
- No changes were required to the logic since `httpx.Response` provides the same `.ok` and `.json()` methods as `requests.Response`.