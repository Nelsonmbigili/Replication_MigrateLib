### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. Replaced `requests.Session` with `httpx.Client`, as `httpx.Client` is the equivalent of `requests.Session`.
2. Updated the `session.get` call to use `httpx.Client.get`.
3. The `httpx` library uses `response.text` to access the decoded content of the response, so replaced `response.content.decode()` with `response.text`.
4. Updated the import statement to remove `requests` and replaced it with `httpx`.

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


session = httpx.Client()


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
    response = session.get("{0}{1}/json".format(pypi_server,
                                                package_name))
    if response.status_code >= 300:
        raise HTTPError(status_code=response.status_code,
                        reason=response.reason)
    return json2package(response.text)
```