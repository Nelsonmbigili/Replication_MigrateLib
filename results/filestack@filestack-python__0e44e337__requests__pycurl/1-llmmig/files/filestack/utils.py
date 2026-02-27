import time
import string
import random
from functools import partial
import pycurl
import io

from filestack import config
from filestack.exceptions import FilestackHTTPError


def unique_id(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class RequestsWrapper:
    """
    This class wraps selected methods from pycurl and adds
    default headers if no headers were specified.
    """
    def __getattr__(self, name):
        if name in ('get', 'post', 'put', 'delete'):
            return partial(self.handle_request, name)
        raise AttributeError(f"'RequestsWrapper' object has no attribute '{name}'")

    def handle_request(self, method, url, *args, **kwargs):
        # Prepare headers
        headers = kwargs.get('headers', config.HEADERS.copy())
        headers['Filestack-Trace-Id'] = '{}-{}'.format(int(time.time()), unique_id())
        headers['Filestack-Trace-Span'] = 'pythonsdk-{}'.format(unique_id())
        headers_list = [f"{key}: {value}" for key, value in headers.items()]

        # Prepare data (if any)
        data = kwargs.get('data', None)

        # Prepare response buffer
        response_buffer = io.BytesIO()

        # Initialize pycurl
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
        curl.setopt(pycurl.HTTPHEADER, headers_list)

        # Set HTTP method
        if method == 'post':
            curl.setopt(pycurl.POST, 1)
            if data:
                curl.setopt(pycurl.POSTFIELDS, data)
        elif method == 'put':
            curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
            if data:
                curl.setopt(pycurl.POSTFIELDS, data)
        elif method == 'delete':
            curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        elif method == 'get':
            curl.setopt(pycurl.HTTPGET, 1)

        # Perform the request
        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            curl.close()
            raise FilestackHTTPError(f"pycurl error: {e}")

        # Close the curl object
        curl.close()

        # Check for HTTP errors
        if status_code < 200 or status_code >= 300:
            raise FilestackHTTPError(f"HTTP error: {status_code}, Response: {response_buffer.getvalue().decode('utf-8')}")

        # Return the response body
        return response_buffer.getvalue().decode('utf-8')


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
