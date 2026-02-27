### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced `import requests` with `import httpx`.
2. **HTTP Methods**: Replaced `requests.get` with `httpx.get`. The method signatures for `httpx.get` are similar to `requests.get`, so no additional changes were needed.
3. **Exception Handling**: Updated the exception handling to use `httpx.RequestError` instead of the generic `Exception`. This is because `httpx` provides a specific exception class for request-related errors.
4. **Behavioral Consistency**: The rest of the code remains unchanged to ensure the same behavior as the original implementation.

### Modified Code
```python
import httpx

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    @classmethod
    def _get_user_info(cls):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        try:
            response = httpx.get(url)
        except httpx.RequestError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_info = response.json().get('result')[0]

    @classmethod
    def _get_user_sub(cls):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        try:
            response = httpx.get(url)
        except httpx.RequestError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_submission = response.json().get('result')

    @classmethod
    def _get_rating_changes(cls):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        try:
            response = httpx.get(url)
        except httpx.RequestError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.rating_changes = response.json().get('result')

    @staticmethod
    def make_request():
        """Makes all the necessary requests to cf API."""
        CFRequestHandler._get_user_info()
        CFRequestHandler._get_user_sub()
        CFRequestHandler._get_rating_changes()
```

### Summary of Changes
- Replaced `requests` with `httpx` for HTTP requests.
- Updated exception handling to use `httpx.RequestError` for better specificity.
- Maintained the original structure and behavior of the code.