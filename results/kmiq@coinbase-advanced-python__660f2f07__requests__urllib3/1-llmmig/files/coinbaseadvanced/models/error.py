"""
Encapsulating error types.
"""

import json
import urllib3


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
    def not_ok_response(cls, response: urllib3.response.HTTPResponse) -> 'CoinbaseAdvancedTradeAPIError':
        """
        Factory Method for Coinbase Advanced errors.
        """

        try:
            # Decode the response data from bytes to string and parse as JSON
            error_result = json.loads(response.data.decode('utf-8'))
        except ValueError:
            # If decoding or JSON parsing fails, use the raw response data
            error_result = {'reason': response.data.decode('utf-8')}

        return cls(error_dict=error_result)
