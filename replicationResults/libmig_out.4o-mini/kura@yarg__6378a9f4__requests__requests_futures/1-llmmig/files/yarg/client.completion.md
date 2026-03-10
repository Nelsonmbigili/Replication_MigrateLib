### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Importing the FutureSession**: Instead of using `requests.Session()`, we now use `requests_futures.sessions.FutureSession()`. This allows us to make asynchronous requests.
2. **Using `submit` Method**: The `get` method is now called using the `submit` method of the `FutureSession`, which returns a `Future` object. This object can be used to retrieve the response once the request is complete.
3. **Handling the Future Object**: We need to call the `result()` method on the `Future` object to get the actual response.

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


import requests_futures.sessions

from .exceptions import HTTPError
from .package import json2package


session = requests_futures.sessions.FutureSession()


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
    future = session.get("{0}{1}/json".format(pypi_server,
                                                package_name))
    response = future.result()
    if response.status_code >= 300:
        raise HTTPError(status_code=response.status_code,
                        reason=response.reason)
    if hasattr(response.content, 'decode'):
        return json2package(response.content.decode())
    else:
        return json2package(response.content)
```