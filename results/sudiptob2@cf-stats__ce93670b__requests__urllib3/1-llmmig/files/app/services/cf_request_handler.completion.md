### Explanation of Changes:
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`, so the `requests` import was removed, and `urllib3` was imported instead.
2. **Creating an HTTP Connection Pool**: `urllib3` requires an HTTP connection pool manager to make requests. A `PoolManager` instance was created and used for all HTTP requests.
3. **Replacing `requests.get`**: The `requests.get` calls were replaced with `urllib3.PoolManager.request` calls. The `method` parameter was set to `"GET"`, and the `url` parameter was passed as required.
4. **Handling JSON Responses**: Unlike `requests`, `urllib3` does not have a built-in `.json()` method. The response body is read using `.data`, and the JSON is parsed using the `json.loads` function from the `json` module.
5. **Error Handling**: `urllib3` raises `urllib3.exceptions.HTTPError` for connection-related issues. This was handled in the `try-except` blocks.

### Modified Code:
```python
import urllib3
import json

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    # Create a PoolManager instance for making HTTP requests
    http = urllib3.PoolManager()

    @classmethod
    def _get_user_info(cls):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        try:
            response = cls.http.request("GET", url)
        except urllib3.exceptions.HTTPError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_info = json.loads(response.data.decode('utf-8')).get('result')[0]

    @classmethod
    def _get_user_sub(cls):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        try:
            response = cls.http.request("GET", url)
        except urllib3.exceptions.HTTPError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_submission = json.loads(response.data.decode('utf-8')).get('result')

    @classmethod
    def _get_rating_changes(cls):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        try:
            response = cls.http.request("GET", url)
        except urllib3.exceptions.HTTPError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.rating_changes = json.loads(response.data.decode('utf-8')).get('result')

    @staticmethod
    def make_request():
        """Makes all the necessary requests to cf API."""
        CFRequestHandler._get_user_info()
        CFRequestHandler._get_user_sub()
        CFRequestHandler._get_rating_changes()
```

### Key Points:
- The `urllib3.PoolManager` instance (`http`) is used to manage HTTP connections.
- The `response.data` is decoded from bytes to a string using `.decode('utf-8')` before parsing it as JSON.
- The `json.loads` function is used to parse the JSON response.
- Error handling was updated to catch `urllib3.exceptions.HTTPError` for connection issues.