### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Response Handling**: The `requests` library's `Response` object is replaced with `aiohttp`'s `ClientResponse` object. This means that methods like `response.text` and `response.status_code` need to be accessed differently.
2. **Asynchronous Context**: Since `aiohttp` is an asynchronous library, the code must be structured to work within an asynchronous context. This typically involves using `async` and `await` keywords.
3. **Initialization of the Client**: The `aiohttp` library requires an `aiohttp.ClientSession` to be created for making requests, which is not needed in `requests`.

The following code reflects these changes while maintaining the original structure and naming conventions.

### Modified Code
```python
'''
navertalk.exceptions module
'''
from __future__ import unicode_literals

class BaseError(Exception):
    """Base Exception class"""

    def __init__(self, message='-'):
        """__init__ method.

        Args:
            - message: str readable message
        """
        self.message = message

    def __repr__(self):
        """
        repr
        """
        return str(self)

    def __str__(self):
        """
        str
        """
        return '<%s [%s]>' % (self.__class__.__name__, self.message)


class NaverTalkApiError(BaseError):
    """
    When Naver Talk failed to build message, NaverTalkApiError raised
    """

    def __init__(self, api_response):
        """__init__ method.

        Args:
            - api_response: ClientResponse class object
        """
        super(NaverTalkApiError, self).__init__(api_response.result_message)

        self._status_code = 200
        self.result_code = api_response.result_code

    @property
    def status_code(self):
        """
        status_code always return 200
        """
        return self._status_code


class NaverTalkApiConnectionError(BaseError):
    """
    When Naver Talk Api server connection failed, NaverTalkApiConnectionError raised
    """

    def __init__(self, response):
        """___init__ method.

        Args:
            - response: ClientResponse class object
        """
        super(NaverTalkApiConnectionError, self).__init__(await response.text())

        self.status_code = response.status
        self.response = response


class NaverTalkPaymentError(BaseError):
    """
    Exception for handling Payment to fail easily
    for example when pay event occurred for some stuff and the stuff running out,
    raise NaverTalkPaymentError and catch exception to make another action
    """
    def __init__(self, message='-'):
        """ __init__ method.

        Args:
            - message:
        """
        super(NaverTalkPaymentError, self).__init__(message)
```

### Note
- The `await` keyword is used in the `NaverTalkApiConnectionError` class to retrieve the text from the `response` object, which is necessary for asynchronous operations.
- The `status_code` is accessed using `response.status` instead of `response.status_code`.