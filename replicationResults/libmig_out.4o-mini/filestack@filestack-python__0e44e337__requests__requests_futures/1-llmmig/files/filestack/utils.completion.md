### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The import statement for `requests` was changed to import `requests_futures.sessions` instead. This is necessary because `requests_futures` provides a `FuturesSession` class that allows for asynchronous requests.
  
2. **Session Initialization**: Instead of using the standard `requests` methods, we now create an instance of `FuturesSession` which allows us to make requests that can be executed asynchronously.

3. **Handling Requests**: The method for making requests was updated to use the `FuturesSession` instance. This involves calling the `session` object to make requests and handling the response differently since it returns a `Future` object.

4. **Response Handling**: The response handling was updated to wait for the future to complete and then check for errors.

Here is the modified code:

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
    This class wraps selected methods from requests package and adds
    default headers if no headers were specified.
    """
    def __init__(self):
        self.session = FuturesSession()

    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        return self.session.__getattribute__(name)

    def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        future = self.session.request(name, *args, **kwargs)
        response = future.result()  # Wait for the request to complete

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

This code now uses `requests_futures` to handle asynchronous HTTP requests while maintaining the original structure and functionality of the code.