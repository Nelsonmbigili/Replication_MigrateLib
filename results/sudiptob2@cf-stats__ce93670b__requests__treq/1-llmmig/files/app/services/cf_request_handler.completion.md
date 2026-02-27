### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Asynchronous Nature of `treq`**: `treq` is an asynchronous library, so the methods that make HTTP requests (`_get_user_info`, `_get_user_sub`, `_get_rating_changes`) were converted to asynchronous methods using `async def`.
2. **Using `treq.get`**: Replaced `requests.get` with `treq.get` for making GET requests.
3. **Handling Responses**: `treq` returns a `Deferred` object, so the response content must be awaited using `await response.json()` after converting the response to JSON.
4. **Error Handling**: The `try-except` block was updated to handle exceptions in an asynchronous context.
5. **Calling Asynchronous Methods**: The `make_request` method was also converted to an asynchronous method to call the other asynchronous methods using `await`.

### Modified Code
```python
import treq
import asyncio

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    @classmethod
    async def _get_user_info(cls):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        try:
            response = await treq.get(url)
            response_json = await response.json()
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_info = response_json.get('result')[0]

    @classmethod
    async def _get_user_sub(cls):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        try:
            response = await treq.get(url)
            response_json = await response.json()
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_submission = response_json.get('result')

    @classmethod
    async def _get_rating_changes(cls):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        try:
            response = await treq.get(url)
            response_json = await response.json()
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.rating_changes = response_json.get('result')

    @staticmethod
    async def make_request():
        """Makes all the necessary requests to cf API."""
        await CFRequestHandler._get_user_info()
        await CFRequestHandler._get_user_sub()
        await CFRequestHandler._get_rating_changes()
```

### Key Notes
- The `make_request` method and all methods that make HTTP requests are now asynchronous (`async def`).
- The `await` keyword is used to handle asynchronous calls to `treq.get` and to process the response.
- The `treq` library requires an asynchronous runtime, so the `make_request` method must be called within an event loop (e.g., using `asyncio.run(CFRequestHandler.make_request())` in the main application).