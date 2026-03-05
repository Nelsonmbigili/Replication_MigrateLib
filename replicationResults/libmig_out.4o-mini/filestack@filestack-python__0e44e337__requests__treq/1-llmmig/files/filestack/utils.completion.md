### Explanation of Changes

To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was changed to import `treq`.
2. **Method Calls**: The method calls to `requests` were replaced with equivalent calls to `treq`. The `get`, `post`, `put`, and `delete` methods are now called from `treq` instead of `requests`.
3. **Error Handling**: The error handling was updated to use `treq.exceptions.HTTPError` instead of `requests.exceptions.HTTPError`.

The overall structure and logic of the code remain unchanged, adhering to the requirement of not altering the original coding style or variable names.

### Modified Code

```python
import time
import string
import random
from functools import partial
import treq as original_requests
from treq.exceptions import HTTPError

from filestack import config
from filestack.exceptions import FilestackHTTPError


def unique_id(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class RequestsWrapper:
    """
    This class wraps selected methods from requests package and adds
    default headers if no headers were specified.
    """
    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        return original_requests.__getattribute__(name)

    def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        requests_method = getattr(original_requests, name)
        response = requests_method(*args, **kwargs)

        try:
            response.raise_for_status()
        except HTTPError as e:
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