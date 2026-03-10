### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `aiohttp`.
2. **Response Handling**: The `requests.Response` object was replaced with `aiohttp.ClientResponse`. The way to check if the response is successful and to parse JSON data has been updated to use `response.status` and `await response.json()`, respectively.
3. **Asynchronous Functions**: Since `aiohttp` is asynchronous, the `from_response` methods were modified to be asynchronous (`async def`) and now require the use of `await` when calling `response.json()`.
4. **Error Handling**: The error handling remains the same, but it is now done in an asynchronous context.

Here is the modified code:

```python
"""
Object models for order related endpoints args and response.
"""

import aiohttp

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
    async def from_response(cls, response: aiohttp.ClientResponse) -> 'EmptyResponse':
        """
        Factory Method that creates an EmptyResponse object from a aiohttp.ClientResponse object.

        Args:
            response (aiohttp.ClientResponse): The response object returned by the API.

        Returns:
            EmptyResponse: An instance of the EmptyResponse class.

        Raises:
            CoinbaseAdvancedTradeAPIError: If the response is not OK.
        """

        if response.status != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = await response.json()
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
    async def from_response(cls, response: aiohttp.ClientResponse) -> 'UnixTime':
        """
        Factory Method.
        """

        if response.status != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = await response.json()
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

This code now uses `aiohttp` for asynchronous HTTP requests, allowing for non-blocking operations in an asynchronous environment.