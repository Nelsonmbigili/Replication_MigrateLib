### Explanation of Changes:
To migrate the code from the `requests` library to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so the methods that use it must be defined as `async` and called using `await`.
2. **HTTP Requests**: Replaced `requests.post` with `aiohttp.ClientSession.post` for making HTTP POST requests.
3. **Response Handling**: In `aiohttp`, the response body must be explicitly read using `await response.text()` or `await response.json()`.
4. **Status Code Check**: Replaced `r.status_code` with `response.status` to check the HTTP status code in `aiohttp`.
5. **Session Management**: Used `aiohttp.ClientSession` to manage HTTP sessions. This requires creating and closing the session properly, which is typically done using an `async with` block.

### Modified Code:
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
import aiohttp

from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
from PyPowerFlex.constants import StoragePoolConstants, VolumeConstants, SnapshotPolicyConstants


LOG = logging.getLogger(__name__)


class PowerFlexUtility(base_client.EntityRequest):
    def __init__(self, token, configuration):
        super(PowerFlexUtility, self).__init__(token, configuration)

    async def send_post_request(self, url, entity, action, params):
        """Helper method to send POST requests using aiohttp."""
        headers = {'Authorization': f'Bearer {self.token}'}
        payload = {
            'entity': entity,
            'action': action,
            'params': params
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response_text = await response.text()
                return response, response_text

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

        response, response_text = await self.send_post_request(self.list_statistics_url,
                                                               entity='StoragePool',
                                                               action=action,
                                                               params=params)
        if response.status != 200:
            msg = ('Failed to list storage pool statistics for PowerFlex. '
                   'Error: {response}'.format(response=response_text))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response_text

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

        response, response_text = await self.send_post_request(self.list_statistics_url,
                                                               entity='Volume',
                                                               action=action,
                                                               params=params)
        if response.status != 200:
            msg = ('Failed to list volume statistics for PowerFlex. '
                   'Error: {response}'.format(response=response_text))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response_text

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

        response, response_text = await self.send_post_request(self.list_statistics_url,
                                                               entity='SnapshotPolicy',
                                                               action=action,
                                                               params=params)
        if response.status != 200:
            msg = ('Failed to list snapshot policy statistics for PowerFlex. '
                   'Error: {response}'.format(response=response_text))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response_text
```

### Key Points:
1. The `send_post_request` method was added to centralize the logic for making POST requests using `aiohttp`.
2. All methods that interact with the HTTP API (`get_statistics_for_all_storagepools`, `get_statistics_for_all_volumes`, and `get_statistics_for_all_snapshot_policies`) were updated to use `await` and the new `send_post_request` method.
3. The `response.status` property is used to check the HTTP status code, and the response body is read using `await response.text()`.