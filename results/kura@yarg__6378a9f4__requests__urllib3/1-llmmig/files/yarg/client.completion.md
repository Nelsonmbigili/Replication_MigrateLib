### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Session Replacement**: The `requests.Session` object was replaced with an `urllib3.PoolManager` object, which provides connection pooling and is the closest equivalent in `urllib3`.
2. **HTTP Request**: The `session.get` method was replaced with the `urllib3.PoolManager.request` method. The `method` parameter was set to `"GET"`, and the URL was passed as an argument.
3. **Response Handling**: The `urllib3` response object does not have a `status_code` or `reason` attribute. Instead:
   - `response.status` was used in place of `response.status_code`.
   - `response.reason` was accessed using `response.reason` (it is available in `urllib3`).
4. **Content Decoding**: The `urllib3` response object provides the raw content as `response.data`. This was decoded using `.decode()` to handle the content properly.
5. **Session Removal**: Since `urllib3` does not use a session object like `requests`, the `session` variable was removed.

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
    response = http.request("GET", "{0}{1}/json".format(pypi_server, package_name))
    if response.status >= 300:
        raise HTTPError(status_code=response.status, reason=response.reason)
    if hasattr(response.data, 'decode'):
        return json2package(response.data.decode())
    else:
        return json2package(response.data)
```