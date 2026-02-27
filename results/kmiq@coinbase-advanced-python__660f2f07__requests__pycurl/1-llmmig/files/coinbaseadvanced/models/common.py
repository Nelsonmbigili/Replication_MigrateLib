"""
Object models for order related endpoints args and response.
"""

import pycurl
import json
from io import BytesIO

from coinbaseadvanced.models.error import CoinbaseAdvancedTradeAPIError


def make_pycurl_request(url: str, method: str = "GET", headers: dict = None, data: dict = None) -> dict:
    """
    Helper function to make HTTP requests using pycurl.

    Args:
        url (str): The URL to send the request to.
        method (str): The HTTP method (e.g., "GET", "POST").
        headers (dict): Optional headers to include in the request.
        data (dict): Optional data to include in the request (for POST/PUT).

    Returns:
        dict: The parsed JSON response.

    Raises:
        CoinbaseAdvancedTradeAPIError: If the HTTP request fails or the response is not OK.
    """
    buffer = BytesIO()
    curl = pycurl.Curl()

    try:
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)

        # Set HTTP method
        if method == "POST":
            curl.setopt(pycurl.POST, 1)
            if data:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(data))
        elif method == "PUT":
            curl.setopt(pycurl.CUSTOMREQUEST, "PUT")
            if data:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(data))
        elif method == "DELETE":
            curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")

        # Set headers
        if headers:
            curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

        # Perform the request
        curl.perform()

        # Check HTTP status code
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        if status_code < 200 or status_code >= 300:
            raise CoinbaseAdvancedTradeAPIError(f"HTTP request failed with status code {status_code}")

        # Parse the response body
        response_body = buffer.getvalue().decode("utf-8")
        return json.loads(response_body)

    finally:
        curl.close()
        buffer.close()


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
    def from_response(cls, url: str, method: str = "GET", headers: dict = None, data: dict = None) -> 'EmptyResponse':
        """
        Factory Method that creates an EmptyResponse object from a pycurl response.

        Args:
            url (str): The URL to send the request to.
            method (str): The HTTP method (e.g., "GET", "POST").
            headers (dict): Optional headers to include in the request.
            data (dict): Optional data to include in the request.

        Returns:
            EmptyResponse: An instance of the EmptyResponse class.

        Raises:
            CoinbaseAdvancedTradeAPIError: If the response is not OK.
        """
        result = make_pycurl_request(url, method, headers, data)
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
    def from_response(cls, url: str, method: str = "GET", headers: dict = None, data: dict = None) -> 'UnixTime':
        """
        Factory Method.
        """
        result = make_pycurl_request(url, method, headers, data)
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
