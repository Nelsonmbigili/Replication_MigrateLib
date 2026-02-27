### Explanation of Changes:
To migrate from the `requests` library to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: Since `aiohttp` is an asynchronous library, the methods that make HTTP requests were converted to `async` methods. This allows the use of `await` for non-blocking calls.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` to make requests. A session is created and used for all HTTP requests.
3. **Error Handling**: The `aiohttp.ClientSession.get` method raises `aiohttp.ClientError` for connection-related issues, so the exception handling was updated accordingly.
4. **JSON Parsing**: The `aiohttp` library provides an `await response.json()` method to parse JSON responses asynchronously.
5. **Static to Async Methods**: The `make_request` method and all methods that make HTTP requests were converted to `async` methods to support asynchronous execution.

Below is the modified code:

---

### Modified Code:
```python
import aiohttp
import asyncio

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    @classmethod
    async def _get_user_info(cls, session):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = await response.json()
                cls.user_info = data.get('result')[0]
        except aiohttp.ClientError:
            raise SystemExit('Could not connect to the codeforces API')

    @classmethod
    async def _get_user_sub(cls, session):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = await response.json()
                cls.user_submission = data.get('result')
        except aiohttp.ClientError:
            raise SystemExit('Could not connect to the codeforces API')

    @classmethod
    async def _get_rating_changes(cls, session):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = await response.json()
                cls.rating_changes = data.get('result')
        except aiohttp.ClientError:
            raise SystemExit('Could not connect to the codeforces API')

    @staticmethod
    async def make_request():
        """Makes all the necessary requests to cf API."""
        async with aiohttp.ClientSession() as session:
            await CFRequestHandler._get_user_info(session)
            await CFRequestHandler._get_user_sub(session)
            await CFRequestHandler._get_rating_changes(session)

```

---

### Key Points:
1. **Session Management**: The `aiohttp.ClientSession` is used as a context manager (`async with`) to ensure proper cleanup of resources.
2. **Asynchronous Methods**: All methods that make HTTP requests are now `async` and use `await` for non-blocking operations.
3. **Error Handling**: The `aiohttp.ClientError` exception is caught to handle connection-related issues.
4. **JSON Parsing**: The `await response.json()` method is used to parse JSON responses asynchronously.

This code is now fully migrated to use `aiohttp` and supports asynchronous execution.