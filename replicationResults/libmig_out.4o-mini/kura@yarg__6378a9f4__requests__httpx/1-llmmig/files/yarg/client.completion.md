### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Session Management**: The `httpx` library does not require a session object for making requests. Instead, we can directly use `httpx.get()` for making requests.
3. **Response Handling**: The way to access the response content and status code remains similar, but we use `response.status_code` and `response.text` instead of `response.content.decode()` for decoding the response content.

### Modified Code
```python
# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2014 Kura
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import httpx

from .exceptions import HTTPError
from .package import json2package


def get(package_name, pypi_server="https://pypi.python.org/pypi/"):
    """
    Construct a request to the PyPI server and returns an instance of
    :class:`yarg.package.Package`.

    :param package_name: case sensitive name of the package on the PyPI server.
    :param pypi_server: (option) URL to the PyPI server.

        >>> import yarg
        >>> package = yarg.get('yarg')
        <Package yarg>
    """
    if not pypi_server.endswith("/"):
        pypi_server = pypi_server + "/"
    response = httpx.get("{0}{1}/json".format(pypi_server,
                                                package_name))
    if response.status_code >= 300:
        raise HTTPError(status_code=response.status_code,
                        reason=response.reason)
    return json2package(response.text)
```