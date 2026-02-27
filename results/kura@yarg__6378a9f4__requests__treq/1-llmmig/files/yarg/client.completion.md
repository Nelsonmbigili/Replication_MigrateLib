### Explanation of Changes:
To migrate the code from `requests` to `treq`, the following changes were made:
1. **Session Replacement**: `treq` does not use sessions like `requests`. Instead, it provides asynchronous HTTP methods directly.
2. **Asynchronous Nature**: `treq` is built on `Twisted` and is asynchronous. The `get` function was modified to be asynchronous using `async def`, and `await` was added where necessary.
3. **Response Handling**: `treq` provides methods like `treq.content()` to retrieve the response body. These methods are asynchronous and require `await`.
4. **Error Handling**: The HTTP status code check was updated to work with `treq`'s response object.
5. **Import Changes**: The `requests` library was replaced with `treq`.

### Modified Code:
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


import treq

from .exceptions import HTTPError
from .package import json2package


async def get(package_name, pypi_server="https://pypi.python.org/pypi/"):
    """
    Construct a request to the PyPI server and returns an instance of
    :class:`yarg.package.Package`.

    :param package_name: case sensitive name of the package on the PyPI server.
    :param pypi_server: (option) URL to the PyPI server.

        >>> import yarg
        >>> package = await yarg.get('yarg')
        <Package yarg>
    """
    if not pypi_server.endswith("/"):
        pypi_server = pypi_server + "/"
    response = await treq.get("{0}{1}/json".format(pypi_server, package_name))
    if response.code >= 300:
        raise HTTPError(status_code=response.code, reason=response.phrase)
    content = await treq.content(response)
    if hasattr(content, 'decode'):
        return json2package(content.decode())
    else:
        return json2package(content)
```

### Key Notes:
1. The `get` function is now asynchronous (`async def`) and must be awaited when called.
2. The `treq.get` method is used instead of `session.get`.
3. The `response.code` and `response.phrase` are used for status code and reason, respectively.
4. The `treq.content()` method is used to retrieve the response body asynchronously.
5. The rest of the code remains unchanged to ensure compatibility with the larger application.