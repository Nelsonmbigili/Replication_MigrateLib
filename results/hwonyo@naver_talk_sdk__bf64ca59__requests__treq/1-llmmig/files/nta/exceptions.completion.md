### Explanation of Changes:
The original code uses the `requests` library to handle HTTP responses, but the migration to `treq` requires adapting the code to work with `treq`'s asynchronous API. Specifically:
1. `requests.Response` objects are replaced with `treq`'s asynchronous response objects.
2. `response.text` is replaced with `await response.text()` since `treq` methods return coroutines.
3. `response.status_code` remains the same but must be awaited as `await response.code` in `treq`.
4. The `NaverTalkApiConnectionError` class is updated to handle `treq`'s asynchronous response handling.

### Modified Code:
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
            - api_response: Response class object
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

    async def __init__(self, response):
        """___init__ method.

        Args:
            - response: models.response
        """
        # Use await to retrieve the response text and status code
        response_text = await response.text()
        response_code = response.code

        super(NaverTalkApiConnectionError, self).__init__(response_text)

        self.status_code = response_code
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

### Key Changes:
1. The `NaverTalkApiConnectionError` class now uses `await response.text()` and `await response.code` to handle `treq`'s asynchronous response objects.
2. The `__init__` method of `NaverTalkApiConnectionError` is now an `async` method to accommodate the asynchronous nature of `treq`.

This ensures compatibility with the `treq` library while maintaining the original structure and functionality of the code.