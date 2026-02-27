### Explanation of Changes
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Import Replacement**: Replaced the `requests` import with `httpx`.
2. **Status Code Check**: Replaced `requests.codes.ok` with `httpx.codes.OK` for checking HTTP status codes.
3. **HTTP Client**: The `httpx` library uses similar syntax for making HTTP requests, so no changes were needed for the `send_get_request` method (assuming it internally handles the HTTP request using `httpx`).

### Modified Code
Here is the updated code after migrating to `httpx`:

```python
# Copyright (c) 2024 Dell Inc. or its subsidiaries.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import httpx
from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
LOG = logging.getLogger(__name__)


class FirmwareRepository(base_client.EntityRequest):
    def get(self, filters=None, limit=None, offset=None, sort=None, related=False, bundles=False, components=False):
        """
        Retrieve all firmware repository with filter, sort, pagination
        :param filters: (Optional) The filters to apply to the results.
        :param limit: (Optional) Page limit.
        :param offset: (Optional) Pagination offset.
        :param sort: (Optional) The field to sort the results by.
        :param related: Whether to include related entities in the response.
        :param bundles: Whether to include bundles in the response.
        :param components: Whether to include components in the response.
        :return: A list of dictionary containing the retrieved firmware repository.
        """
        params = dict(
            filter=filters,
            sort=sort,
            offset=offset,
            limit=limit,
            related=related,
            bundles=bundles,
            components=components
        )
        r, response = self.send_get_request(utils.build_uri_with_params(self.firmware_repository_url, **params))
        if r.status_code != httpx.codes.OK:
            msg = (f'Failed to retrieve firmware repository. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return response
```

### Summary of Changes
- Replaced `requests` with `httpx` in the import statement.
- Updated `requests.codes.ok` to `httpx.codes.OK` for status code comparison.

No other changes were made to ensure the code remains consistent with the original structure and functionality.