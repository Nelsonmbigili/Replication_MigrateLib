### Explanation of Changes
The migration from the `requests` library to the `treq` library involves the following changes:
1. **Asynchronous Nature of `treq`**: Unlike `requests`, `treq` is an asynchronous library. This means that functions using `treq` must be asynchronous (`async def`) and must use `await` for asynchronous calls.
2. **HTTP Status Code Check**: In `requests`, `r.status_code` is used to check the HTTP status code. In `treq`, you need to use `response.code` to access the status code.
3. **Response Content**: In `requests`, `r.json()` is used to parse JSON responses. In `treq`, you need to use `await response.json()` to get the JSON content.
4. **Import Changes**: The `requests` import is replaced with `treq`.

Below is the modified code with these changes applied.

---

### Modified Code
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

import treq

from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
from PyPowerFlex.constants import StoragePoolConstants, VolumeConstants, SnapshotPolicyConstants


LOG = logging.getLogger(__name__)


class PowerFlexUtility(base_client.EntityRequest):
    def __init__(self, token, configuration):
        super(PowerFlexUtility, self).__init__(token, configuration)

    async def get_statistics_for_all_storagepools(self, ids=None, properties=None):
        """list storagepool statistics for PowerFlex.

        :param ids: list
        :param properties: list
        :return: dict
        """

        action = 'querySelectedStatistics'
        version = self.get_api_version()
        default_properties = StoragePoolConstants.DEFAULT_STATISTICS_PROPERTIES
        if version != '3.5':
            default_properties = default_properties + StoragePoolConstants.DEFAULT_STATISTICS_PROPERTIES_ABOVE_3_5
        params = {'properties': default_properties if properties is None else properties}
        if ids is None:
            params['allIds'] = ""
        else:
            params['ids'] = ids

        r, response = await self.send_post_request(self.list_statistics_url,
                                                   entity='StoragePool',
                                                   action=action,
                                                   params=params)
        if r.code != 200:  # treq uses `response.code` for status codes
            msg = ('Failed to list storage pool statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    async def get_statistics_for_all_volumes(self, ids=None, properties=None):
        """list volume statistics for PowerFlex.

        :param ids: list
        :param properties: list
        :return: dict
        """

        action = 'querySelectedStatistics'

        params = {'properties': VolumeConstants.DEFAULT_STATISTICS_PROPERTIES if properties is None else properties}
        if ids is None:
            params['allIds'] = ""
        else:
            params['ids'] = ids

        r, response = await self.send_post_request(self.list_statistics_url,
                                                   entity='Volume',
                                                   action=action,
                                                   params=params)
        if r.code != 200:  # treq uses `response.code` for status codes
            msg = ('Failed to list volume statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    async def get_statistics_for_all_snapshot_policies(self, ids=None, properties=None):
        """list snapshot policy statistics for PowerFlex.

        :param ids: list
        :param properties: list
        :return: dict
        """

        action = 'querySelectedStatistics'

        params = {'properties': SnapshotPolicyConstants.DEFAULT_STATISTICS_PROPERTIES if properties is None else properties}
        if ids is None:
            params['allIds'] = ""
        else:
            params['ids'] = ids

        r, response = await self.send_post_request(self.list_statistics_url,
                                                   entity='SnapshotPolicy',
                                                   action=action,
                                                   params=params)
        if r.code != 200:  # treq uses `response.code` for status codes
            msg = ('Failed to list snapshot policy statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response
```

---

### Key Notes
1. **Asynchronous Methods**: All methods that interact with `treq` are now asynchronous (`async def`) and use `await` for asynchronous calls.
2. **Status Code Check**: The `r.status_code` check is replaced with `r.code` in `treq`.
3. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the larger application.