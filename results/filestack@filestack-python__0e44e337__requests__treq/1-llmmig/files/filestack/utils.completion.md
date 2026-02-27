### Explanation of Changes:
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Replaced `requests` with `treq`**:
   - The `requests` library is synchronous, while `treq` is asynchronous. Therefore, the `handle_request` method was modified to use `async` and `await` to handle asynchronous requests.
   - The `treq` library does not have a `raise_for_status` method. Instead, we manually check the HTTP status code and raise an exception if the status code indicates an error.
2. **Modified the `RequestsWrapper` class**:
   - The `handle_request` method now uses `treq`'s `get`, `post`, `put`, and `delete` methods.
   - Since `treq` returns a `Deferred` object, the response content is accessed using `await response.text()` or similar methods.
3. **Updated exception handling**:
   - The `HTTPError` from `requests` was replaced with a manual check for HTTP status codes, raising a `FilestackHTTPError` if the response status code is not in the 2xx range.
4. **Added `async` to the `handle_request` method**:
   - Since `treq` is asynchronous, the `handle_request` method was updated to be an `async` function.

### Modified Code:
```python
import time
import string
import random
from functools import partial
import treq
from filestack import config
from filestack.exceptions import FilestackHTTPError


def unique_id(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class RequestsWrapper:
    """
    This class wraps selected methods from treq package and adds
    default headers if no headers were specified.
    """
    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        raise AttributeError(f"'RequestsWrapper' object has no attribute '{name}'")

    async def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        treq_method = getattr(treq, name)
        response = await treq_method(*args, **kwargs)

        if response.status_code < 200 or response.status_code >= 300:
            error_text = await response.text()
            raise FilestackHTTPError(error_text)

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

### Key Notes:
- The `RequestsWrapper` class now uses `treq`'s asynchronous methods (`get`, `post`, `put`, `delete`).
- The `handle_request` method is now an `async` function, and any code calling it must also be asynchronous or use an event loop to execute it.
- The `FilestackHTTPError` is raised manually by checking the response's status code, as `treq` does not provide a `raise_for_status` method.
- The rest of the code remains unchanged, as it is unrelated to the migration from `requests` to `treq`.