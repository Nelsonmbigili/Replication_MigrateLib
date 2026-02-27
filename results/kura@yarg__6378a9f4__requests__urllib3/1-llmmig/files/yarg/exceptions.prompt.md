The following Python code currently uses the library "requests" version 2.32.3.
Migrate this code to use the library "urllib3" version 2.4.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "urllib3".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "urllib3".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
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


from requests.exceptions import HTTPError as RHTTPError


class YargException(Exception):
    pass


class HTTPError(YargException, RHTTPError):
    """
    A catchall HTTPError exception to handle HTTP errors
    when using :meth:`yarg.get`.

    This exception is also loaded at :class:`yarg.HTTPError`
    for ease of access.

    :member: status_code
    """

    def __init__(self, *args, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        if hasattr(self, 'status_code'):
            setattr(self, 'errno', self.status_code)
        if hasattr(self, 'reason'):
            setattr(self, 'message', self.reason)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if hasattr(self, 'status_code') and hasattr(self, 'reason'):
            return "<HTTPError {0} {1}>".format(self.status_code, self.reason)
        return "<HTTPError>"

```