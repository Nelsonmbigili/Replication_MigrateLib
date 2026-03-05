### Explanation of Changes
To migrate from the `requests` library to `pycurl`, the primary changes involve replacing the HTTP request handling provided by `requests` with the equivalent functionality in `pycurl`. Since the original code does not contain any HTTP request logic, the migration will focus on how to set up a basic request using `pycurl`. 

In `pycurl`, we need to create a `CURL` object, set the necessary options (like URL, HTTP method, etc.), and perform the request. The response handling will also differ, as `pycurl` does not automatically handle JSON or response content like `requests` does. Instead, we will need to manually handle the response data.

However, since the provided code does not include any HTTP request logic, the migration will be minimal and will focus on setting up the structure for future requests using `pycurl`.

### Modified Code
```python
from typing import Any
import pycurl
from io import BytesIO

from requests.structures import CaseInsensitiveDict


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass

# Example function to demonstrate how to use pycurl for a GET request
def make_request(url: str):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    
    try:
        c.perform()
        status_code = c.getinfo(c.RESPONSE_CODE)
        response_data = buffer.getvalue().decode('utf-8')
        return status_code, response_data
    except pycurl.error as e:
        raise ApiException(data=str(e), status_code=e.args[0])
    finally:
        c.close()
```

In this modified code, I added a function `make_request` to demonstrate how to perform an HTTP GET request using `pycurl`. This function initializes a `CURL` object, sets the URL, and writes the response to a buffer. It also handles exceptions and closes the `CURL` object properly.