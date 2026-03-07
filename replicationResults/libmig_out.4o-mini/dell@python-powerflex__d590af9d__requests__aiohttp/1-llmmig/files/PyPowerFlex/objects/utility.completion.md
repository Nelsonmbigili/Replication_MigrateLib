### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp` for asynchronous HTTP requests.
2. **Asynchronous Functions**: The methods that perform HTTP requests were modified to be asynchronous. This involved adding the `async` keyword to the method definitions and using `await` for the HTTP calls.
3. **Session Management**: Instead of directly calling `requests.post`, we created an `aiohttp.ClientSession` to manage the session for making requests.
4. **Response Handling**: The response handling was adjusted to work with `aiohttp`, which requires using `await response.json()` to get the JSON data from the response.
5. **Error Handling**: The error handling was updated to check the response status using `response.status` instead of `r.status_code`.

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
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import aiohttp

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

        async with aiohttp.ClientSession() as session:
            async with session.post(self.list_statistics_url, json={'entity': 'StoragePool', 'action': action, 'params': params}) as response:
                if response.status != 200:
                    msg = ('Failed to list storage pool statistics for PowerFlex. '
                           'Error: {response}'.format(response=await response.text()))
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)

                return await response.json()

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

        async with aiohttp.ClientSession() as session:
            async with session.post(self.list_statistics_url, json={'entity': 'Volume', 'action': action, 'params': params}) as response:
                if response.status != 200:
                    msg = ('Failed to list volume statistics for PowerFlex. '
                           'Error: {response}'.format(response=await response.text()))
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)

                return await response.json()

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

        async with aiohttp.ClientSession() as session:
            async with session.post(self.list_statistics_url, json={'entity': 'SnapshotPolicy', 'action': action, 'params': params}) as response:
                if response.status != 200:
                    msg = ('Failed to list snapshot policy statistics for PowerFlex. '
                           'Error: {response}'.format(response=await response.text()))
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)

                return await response.json()
```