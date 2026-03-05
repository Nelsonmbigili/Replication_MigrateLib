import time
import string
import random
from functools import partial
import pycurl
from io import BytesIO
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
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        url = args[0] if args else ''
        headers = [f"{key}: {value}" for key, value in kwargs['headers'].items()]

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.setopt(c.HTTPHEADER, headers)

        if name == 'post':
            c.setopt(c.POST, 1)
            if 'data' in kwargs:
                c.setopt(c.POSTFIELDS, kwargs['data'])
        elif name == 'put':
            c.setopt(c.CUSTOMREQUEST, 'PUT')
            if 'data' in kwargs:
                c.setopt(c.POSTFIELDS, kwargs['data'])
        elif name == 'delete':
            c.setopt(c.CUSTOMREQUEST, 'DELETE')

        try:
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code != 200:
                raise FilestackHTTPError(buffer.getvalue().decode('utf-8'))
        except pycurl.error as e:
            raise FilestackHTTPError(str(e))
        finally:
            c.close()

        return buffer.getvalue().decode('utf-8')


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
