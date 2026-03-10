import time
import string
import random
from functools import partial
import aiohttp
from aiohttp import ClientError

from filestack import config
from filestack.exceptions import FilestackHTTPError


def unique_id(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class RequestsWrapper:
    """
    This class wraps selected methods from aiohttp package and adds
    default headers if no headers were specified.
    """
    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    async def handle_request(self, name, *args, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = config.HEADERS
            kwargs['headers']['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
            kwargs['headers']['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())

        async with aiohttp.ClientSession() as session:
            try:
                if name == 'get':
                    response = await session.get(*args, **kwargs)
                elif name == 'post':
                    response = await session.post(*args, **kwargs)
                elif name == 'put':
                    response = await session.put(*args, **kwargs)
                elif name == 'delete':
                    response = await session.delete(*args, **kwargs)
                else:
                    raise ValueError(f"Unsupported request method: {name}")

                response.raise_for_status()
            except ClientError as e:
                raise FilestackHTTPError(await response.text()) from e

            return response


requests = RequestsWrapper()


async def return_transform_task(transformation, params):
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
