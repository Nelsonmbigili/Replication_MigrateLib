import time
import string
import random
from functools import partial
import urllib3
from urllib3.exceptions import HTTPError

from filestack import config
from filestack.exceptions import FilestackHTTPError


def unique_id(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class RequestsWrapper:
    """
    This class wraps selected methods from urllib3 package and adds
    default headers if no headers were specified.
    """
    def __init__(self):
        self.http = urllib3.PoolManager()

    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        raise AttributeError(f"'RequestsWrapper' object has no attribute '{name}'")

    def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        # Map method name to urllib3 method
        if name == 'get':
            response = self.http.request('GET', *args, **kwargs)
        elif name == 'post':
            response = self.http.request('POST', *args, **kwargs)
        elif name == 'put':
            response = self.http.request('PUT', *args, **kwargs)
        elif name == 'delete':
            response = self.http.request('DELETE', *args, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {name}")

        # Check for HTTP errors
        if response.status >= 400:
            raise FilestackHTTPError(response.data.decode('utf-8'))

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
