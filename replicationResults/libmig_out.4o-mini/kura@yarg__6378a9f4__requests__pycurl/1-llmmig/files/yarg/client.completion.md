### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several key changes were made:

1. **Session Management**: The `requests.Session()` object was removed since `pycurl` does not have a session management feature like `requests`. Instead, we create a new `pycurl.Curl()` object for each request.

2. **Making Requests**: The `session.get()` method was replaced with `pycurl` methods to set the URL and perform the request. We use `setopt()` to configure the request options.

3. **Handling Response**: The response handling is different in `pycurl`. We need to set up a callback function to capture the response data since `pycurl` does not return the response directly like `requests`.

4. **Error Handling**: The error handling was adapted to check for HTTP errors using the `curl.getinfo(curl.RESPONSE_CODE)` method.

5. **Decoding Response**: The response data is captured in a buffer and then decoded accordingly.

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


import pycurl
from io import BytesIO

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
    
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, "{0}{1}/json".format(pypi_server, package_name))
    curl.setopt(curl.WRITEDATA, buffer)
    curl.perform()
    
    response_code = curl.getinfo(curl.RESPONSE_CODE)
    curl.close()
    
    if response_code >= 300:
        raise HTTPError(status_code=response_code, reason='HTTP Error')
    
    response_content = buffer.getvalue()
    if hasattr(response_content, 'decode'):
        return json2package(response_content.decode())
    else:
        return json2package(response_content)
``` 

This code now uses `pycurl` to perform HTTP requests while maintaining the original structure and functionality of the code.