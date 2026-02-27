### Explanation of Changes:
1. The `requests` library was replaced with `urllib3`. Specifically:
   - The `requests.exceptions.HTTPError` was replaced with `urllib3.exceptions.HTTPError`.
2. The import statement for `requests.exceptions.HTTPError` was updated to import `HTTPError` from `urllib3.exceptions`.
3. No other changes were made to the code, as the functionality and structure remain the same.

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


from urllib3.exceptions import HTTPError as UHTTPError


class YargException(Exception):
    pass


class HTTPError(YargException, UHTTPError):
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