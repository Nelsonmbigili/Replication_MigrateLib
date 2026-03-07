### Explanation of Changes
To migrate the code from using the `urllib3` library to the `httpx` library, the following changes were made:

1. **Import Statements**: The import statement for `urllib3` was replaced with the import statement for `httpx`.
2. **Warning Handling**: The `InsecureRequestWarning` handling was removed, as `httpx` does not require explicit disabling of SSL warnings in the same way `urllib3` does.
3. **Functionality**: The code does not include any actual HTTP requests, so the migration primarily involves changing the import statements and removing the warning handling.

### Modified Code
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