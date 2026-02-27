The following Python code currently uses the library "requests" version 2.32.3.
Migrate this code to use the library "treq" version 24.9.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "treq".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "treq".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
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

    def __init__(self, response):
        """___init__ method.

        Args:
            - response: models.response
        """
        super(NaverTalkApiConnectionError, self).__init__(response.text)

        self.status_code = response.status_code
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