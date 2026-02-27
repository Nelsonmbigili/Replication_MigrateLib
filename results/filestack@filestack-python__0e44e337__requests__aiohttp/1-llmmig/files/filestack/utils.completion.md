### Explanation of Changes:
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Nature**: `aiohttp` is an asynchronous library, so the `handle_request` method was modified to be an `async` function. This required the use of `async def` and `await` for asynchronous operations.
2. **Session Management**: `aiohttp` uses `aiohttp.ClientSession` for making requests. A session is created and reused for all requests to improve performance.
3. **Error Handling**: `aiohttp` raises `aiohttp.ClientResponseError` for HTTP errors, which replaces `requests.exceptions.HTTPError`.
4. **Response Handling**: The response content is accessed using `await response.text()` since `aiohttp` operations are asynchronous.
5. **Headers**: The headers are passed in the same way as in `requests`.

### Modified Code:
```python
import time
import string
import random
from functools import partial
import aiohttp
from aiohttp import ClientResponseError

from filestack import config
from filestack.exceptions import FilestackHTTPError


def unique_id(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class RequestsWrapper:
    """
    This class wraps selected methods from aiohttp package and adds
    default headers if no headers were specified.
    """
    def __init__(self):
        self.session = aiohttp.ClientSession()

    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        raise AttributeError(f"'RequestsWrapper' object has no attribute '{name}'")

    async def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        aiohttp_method = getattr(self.session, name)
        try:
            async with aiohttp_method(*args, **kwargs) as response:
                if response.status >= 400:
                    raise FilestackHTTPError(await response.text())
                return await response.text()
        except ClientResponseError as e:
            raise FilestackHTTPError(str(e)) from e

    async def close(self):
        await self.session.close()


requests = RequestsWrapper()


def return_transform_task(transformation, params):
    transform_tasks = []

    for key, value in params.items():
        if isinstance(value, list):
            value = str(value).replace("'", "").replace('"', '').replace(" ", "")
        if isinstance(value, bool):
            value = str(value).lower()

        transform_tasks.append('{}:{}'.format(key, value))

    transform_tasks = sorted(transform_tasks)

    if len(transform_tasks) > 0:
        transformation_url = '{}={}'.format(transformation, ','.join(transform_tasks))
    else:
        transformation_url = transformation

    return transformation_url
```

### Notes:
1. **Session Cleanup**: Since `aiohttp.ClientSession` needs to be closed after use, an `async close` method was added to the `RequestsWrapper` class. Ensure that `requests.close()` is called when the application shuts down.
2. **Asynchronous Usage**: The `handle_request` method is now asynchronous, so any code calling it must use `await`. This may require changes in the calling code to support asynchronous execution.
3. **Error Handling**: The `FilestackHTTPError` is raised with the response text if the HTTP status code indicates an error. This behavior matches the original code.