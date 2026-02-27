### Explanation of Changes
To migrate the code from using the `requests` library to `httpx`, the following changes were made:
1. **Library Import**: Replaced `requests` with `httpx`. The `httpx` library provides similar functionality but with some differences in method signatures and behavior.
2. **Exception Handling**: Replaced `requests.exceptions.HTTPError` with `httpx.HTTPStatusError` for handling HTTP errors.
3. **Request Methods**: Updated the `getattr` method to use `httpx` methods (`httpx.get`, `httpx.post`, etc.) instead of `requests`.
4. **Request Execution**: Updated the `handle_request` method to use `httpx` for making HTTP requests.
5. **Response Error Handling**: Adjusted the error handling to use `httpx`'s `raise_for_status()` method, which raises an `httpx.HTTPStatusError` if the response status code indicates an error.

### Modified Code
```python
import time
import string
import random
from functools import partial
import httpx as original_httpx
from httpx import HTTPStatusError

from filestack import config
from filestack.exceptions import FilestackHTTPError


def unique_id(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class RequestsWrapper:
    """
    This class wraps selected methods from httpx package and adds
    default headers if no headers were specified.
    """
    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        return original_httpx.__getattribute__(name)

    def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        httpx_method = getattr(original_httpx, name)
        response = httpx_method(*args, **kwargs)

        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            raise FilestackHTTPError(response.text) from e

        return response


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

### Key Notes
- The `httpx` library is asynchronous by default, but the above code uses its synchronous API (e.g., `httpx.get`, `httpx.post`) to match the behavior of `requests`.
- The `httpx.HTTPStatusError` exception is raised by `response.raise_for_status()` when the response status code indicates an error, similar to `requests.exceptions.HTTPError`.
- No other parts of the code were modified to ensure compatibility with the rest of the application.