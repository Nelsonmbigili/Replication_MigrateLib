### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. Replaced the `requests` library with `pycurl` for HTTP requests.
2. Used `pycurl.Curl` to perform HTTP methods (`GET`, `POST`, `PUT`, `DELETE`).
3. Replaced `requests`'s `raise_for_status` with manual HTTP status code checks, as `pycurl` does not provide a direct equivalent.
4. Used `io.BytesIO` to capture the response body from `pycurl`.
5. Updated the `handle_request` method to configure `pycurl` options for headers, HTTP methods, and other parameters.
6. Removed the `requests.exceptions.HTTPError` import and replaced it with manual error handling for HTTP status codes.

### Modified Code:
```python
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
```

### Key Notes:
1. The `pycurl` library requires more manual configuration compared to `requests`. For example, setting headers, HTTP methods, and capturing the response body all require explicit setup.
2. The `handle_request` method now uses `pycurl.Curl` to perform HTTP requests and captures the response in a `BytesIO` buffer.
3. Error handling for HTTP status codes is done manually since `pycurl` does not provide a `raise_for_status` equivalent.
4. The rest of the code remains unchanged, as the migration only affects the HTTP request handling logic.