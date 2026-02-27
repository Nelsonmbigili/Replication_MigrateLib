### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Request Handling**: Updated the `requests.get` calls to use `session.get` (from `FuturesSession`) and handled the `.result()` method to retrieve the response synchronously after the asynchronous request is made.
4. **Error Handling**: Wrapped the `.result()` call in a `try-except` block to handle potential exceptions during the resolution of the future.

### Modified Code:
```python
from requests_futures.sessions import FuturesSession

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    # Initialize a FuturesSession for asynchronous requests
    session = FuturesSession()

    @classmethod
    def _get_user_info(cls):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        try:
            future = cls.session.get(url)  # Asynchronous request
            response = future.result()  # Wait for the result
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_info = response.json().get('result')[0]

    @classmethod
    def _get_user_sub(cls):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        try:
            future = cls.session.get(url)  # Asynchronous request
            response = future.result()  # Wait for the result
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_submission = response.json().get('result')

    @classmethod
    def _get_rating_changes(cls):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        try:
            future = cls.session.get(url)  # Asynchronous request
            response = future.result()  # Wait for the result
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.rating_changes = response.json().get('result')

    @staticmethod
    def make_request():
        """Makes all the necessary requests to cf API."""
        CFRequestHandler._get_user_info()
        CFRequestHandler._get_user_sub()
        CFRequestHandler._get_rating_changes()
```

### Key Notes:
- The `FuturesSession` class from `requests_futures` allows for asynchronous HTTP requests. However, since the original code processes the response synchronously, the `.result()` method is used to block until the request completes.
- The migration ensures that the behavior of the code remains consistent with the original implementation while leveraging `requests_futures`.