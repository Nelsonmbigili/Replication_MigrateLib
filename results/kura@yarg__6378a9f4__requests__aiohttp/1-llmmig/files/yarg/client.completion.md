### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Session Management**: Replaced `requests.Session` with `aiohttp.ClientSession`. Since `aiohttp` is asynchronous, the session must be created and used within an `async` context.
2. **HTTP Requests**: Replaced `session.get` with `session.get` from `aiohttp`, which is an asynchronous method. This requires the use of `await`.
3. **Response Handling**: Replaced `response.content` with `await response.read()` to handle the asynchronous nature of `aiohttp`.
4. **Error Handling**: Checked the `response.status` instead of `response.status_code` for HTTP status codes.
5. **Function Signature**: Updated the `get` function to be asynchronous (`async def`) to accommodate the asynchronous nature of `aiohttp`.
6. **Usage Note**: Since the function is now asynchronous, it must be called using `await` in an asynchronous context.

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


import aiohttp

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
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{pypi_server}{package_name}/json") as response:
            if response.status >= 300:
                raise HTTPError(status_code=response.status,
                                reason=response.reason)
            content = await response.read()
            if hasattr(content, 'decode'):
                return json2package(content.decode())
            else:
                return json2package(content)
```

### Key Notes
1. **Asynchronous Context**: The `get` function is now asynchronous and must be called using `await` in an `async` function or context.
2. **Session Management**: The `aiohttp.ClientSession` is used within an `async with` block to ensure proper cleanup of resources.
3. **Error Handling**: The `response.status` is used to check for HTTP errors, as `aiohttp` does not use `response.status_code`.

This code is now fully migrated to use `aiohttp` version 3.11.16.