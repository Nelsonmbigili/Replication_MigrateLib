### Explanation of Changes:
1. **Library Import Replacement**: Replaced `urllib3` with `httpx` since we are migrating to the `httpx` library.
2. **Warning Suppression**: `httpx` does not have a direct equivalent to `urllib3.disable_warnings(InsecureRequestWarning)`. Instead, we use `httpx`'s `verify=False` parameter in requests to suppress SSL verification warnings. However, since the provided code does not include any actual requests, this part is omitted for now.
3. **Removed `urllib3`-specific Code**: Removed the `urllib3.disable_warnings(InsecureRequestWarning)` line, as it is not applicable to `httpx`.

Below is the modified code:

### Modified Code:
```python
"""
The Pitt API, to access workable data of the University of Pittsburgh
Copyright (C) 2015 Ritwik Gupta

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# grequests monkey-patches ssl, but this must be done before all other imports,
# or else we may get a MonkeyPatchWarning or a RecursionError
# See https://github.com/spyoungtech/grequests/issues/150 and https://github.com/gevent/gevent/issues/1016
from gevent import monkey

monkey.patch_all(thread=False, select=False)

import httpx
```