### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Importing `requests_futures`**: The `requests_futures` library was imported, and the `FuturesSession` class was used to enable asynchronous requests.
2. **Replacing `requests` methods**: The `requests` methods (`get`, `post`, `put`, `delete`) were replaced with their asynchronous counterparts from `FuturesSession`.
3. **Session Initialization**: A `FuturesSession` instance was created and used in the `RequestsWrapper` class to handle requests.
4. **Handling Futures**: Since `requests_futures` returns a `Future` object, the `.result()` method was called to retrieve the actual response object. This ensures compatibility with the existing error handling and response processing logic.

### Modified Code
```python
import time
import string
import random
from functools import partial
from requests_futures.sessions import FuturesSession
from requests.exceptions import HTTPError

from filestack import config
from filestack.exceptions import FilestackHTTPError


def unique_id(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class RequestsWrapper:
    """
    This class wraps selected methods from requests_futures package and adds
    default headers if no headers were specified.
    """
    def __init__(self):
        self.session = FuturesSession()

    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        return getattr(self.session, name)

    def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        requests_method = getattr(self.session, name)
        future = requests_method(*args, **kwargs)
        response = future.result()  # Wait for the response to complete and retrieve it

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

### Key Points
- The `FuturesSession` class from `requests_futures` is used to enable asynchronous requests.
- The `.result()` method is called on the `Future` object to block until the request is complete and retrieve the response.
- The rest of the code remains unchanged to ensure compatibility with the existing application logic.