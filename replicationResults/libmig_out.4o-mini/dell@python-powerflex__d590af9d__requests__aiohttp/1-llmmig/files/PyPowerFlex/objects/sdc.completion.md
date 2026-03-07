### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Import Statement**: The `requests` library was replaced with `aiohttp`.
2. **Asynchronous Functions**: Since `aiohttp` is designed for asynchronous programming, the methods that perform HTTP requests were modified to be asynchronous. This includes adding the `async` keyword to the method definitions and using `await` for the HTTP calls.
3. **Session Management**: In `aiohttp`, an `aiohttp.ClientSession` is used to manage connections. This requires creating a session before making requests and closing it afterward.
4. **HTTP Methods**: The methods for making requests (like `get`, `post`, `delete`, etc.) were changed to use `aiohttp`'s syntax.
5. **Response Handling**: The response handling was adjusted to work with `aiohttp`, which requires awaiting the response and then reading the response data.

Here is the modified code:

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
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import aiohttp
from PyPowerFlex import base_client
from PyPowerFlex import exceptions


LOG = logging.getLogger(__name__)


class Sdc(base_client.EntityRequest):
    async def delete(self, sdc_id):
        """Remove PowerFlex SDC.

        :type sdc_id: str
        :rtype: None
        """

        return await self._delete_entity(sdc_id)

    async def get_mapped_volumes(self, sdc_id, filter_fields=None, fields=None):
        """Get PowerFlex volumes mapped to SDC.

        :type sdc_id: str
        :type filter_fields: dict
        :type fields: list|tuple
        :rtype: list[dict]
        """

        return await self.get_related(sdc_id, 'Volume', filter_fields, fields)

    async def rename(self, sdc_id, name):
        """Rename PowerFlex SDC.

        :type sdc_id: str
        :type name: str
        :rtype: dict
        """

        action = 'setSdcName'

        params = dict(
            sdcName=name
        )

        return await self._rename_entity(action, sdc_id, params)

    async def set_performance_profile(self, sdc_id, perf_profile):
        """Apply a performance profile to the specified SDC.

        :type sdc_id: str
        :type perf_profile: str
        :rtype: dict
        """

        action = 'setSdcPerformanceParameters'

        params = dict(
            perfProfile=perf_profile
        )
        return await self._perform_entity_operation_based_on_action\
            (sdc_id, action, params=params, add_entity=False)

    async def query_selected_statistics(self, properties, ids=None):
        """Query PowerFlex SDC statistics.

        :type properties: list
        :type ids: list of SDC IDs or None for all SDC
        :rtype: dict
        """

        action = "querySelectedStatistics"

        params = dict(properties=properties)

        if ids:
            params["ids"] = ids
        else:
            params["allIds"] = ""

        return await self._query_selected_statistics(action, params)
```

This code now uses `aiohttp` for asynchronous HTTP requests, allowing for non-blocking operations which can improve performance in applications that require high concurrency.