### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp`, which is designed for asynchronous HTTP requests.
2. **Creating an Async Session**: Instead of using `requests.Session()`, we create an `aiohttp.ClientSession()` which is used for making requests.
3. **Asynchronous Function**: The `get` function was modified to be asynchronous by adding the `async` keyword and using `await` for the request call.
4. **Making the Request**: The `session.get()` method is replaced with `session.get()` in an asynchronous context, and we await the response.
5. **Reading the Response**: The response content is read asynchronously using `await response.text()` instead of directly accessing `response.content`.

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
        async with session.get("{0}{1}/json".format(pypi_server,
                                                    package_name)) as response:
            if response.status >= 300:
                raise HTTPError(status_code=response.status,
                                reason=response.reason)
            content = await response.text()
            return json2package(content)
``` 

This code now uses `aiohttp` for asynchronous HTTP requests while maintaining the original structure and functionality of the code.