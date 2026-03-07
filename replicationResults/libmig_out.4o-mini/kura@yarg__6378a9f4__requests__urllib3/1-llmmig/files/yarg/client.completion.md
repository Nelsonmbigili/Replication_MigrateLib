### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Session Management**: The `requests.Session()` object was replaced with `urllib3.PoolManager()`, which is used to manage connections in `urllib3`.
2. **Making Requests**: The `session.get()` method was replaced with `http.request('GET', ...)`, where `http` is an instance of `urllib3.PoolManager()`.
3. **Response Handling**: The response object from `urllib3` does not have a `status_code` or `reason` attributes like `requests`. Instead, we check the `status` attribute for the HTTP status code and use `data` to access the response content.
4. **Decoding Content**: The content from `urllib3` is already in bytes, so we can directly decode it if necessary.

Here is the modified code:

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


import urllib3

from .exceptions import HTTPError
from .package import json2package


http = urllib3.PoolManager()


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
    response = http.request('GET', "{0}{1}/json".format(pypi_server,
                                                package_name))
    if response.status >= 300:
        raise HTTPError(status_code=response.status,
                        reason=response.data.decode('utf-8'))
    if hasattr(response.data, 'decode'):
        return json2package(response.data.decode())
    else:
        return json2package(response.data)
```