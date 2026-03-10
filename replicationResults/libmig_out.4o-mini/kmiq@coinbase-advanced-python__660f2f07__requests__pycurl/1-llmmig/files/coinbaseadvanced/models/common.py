"""
Object models for order related endpoints args and response.
"""

import pycurl
import json
from io import BytesIO
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
    def from_response(cls, url: str) -> 'EmptyResponse':
        """
        Factory Method that creates an EmptyResponse object from a pycurl response.

        Args:
            url (str): The URL to send the request to.

        Returns:
            EmptyResponse: An instance of the EmptyResponse class.

        Raises:
            CoinbaseAdvancedTradeAPIError: If the response is not OK.
        """
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.FOLLOWLOCATION, True)
        c.perform()
        
        http_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        if http_code != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(http_code)

        result = json.loads(buffer.getvalue().decode('utf-8'))
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
    def from_response(cls, url: str) -> 'UnixTime':
        """
        Factory Method.
        """

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.FOLLOWLOCATION, True)
        c.perform()
        
        http_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        if http_code != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(http_code)

        result = json.loads(buffer.getvalue().decode('utf-8'))
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
