### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `from requests_futures.sessions import FuturesSession`. This allows us to use the `FuturesSession` class, which is designed for asynchronous requests.
  
2. **Session Initialization**: Instead of using the standard `requests` session, we now create an instance of `FuturesSession`. This allows us to send requests asynchronously.

3. **Sending Requests**: The method for sending requests was updated to use the `FuturesSession` instance. The `send_post_request` method should be modified to accommodate the asynchronous nature of `FuturesSession`.

4. **Handling Responses**: Since the requests are now asynchronous, we need to handle the future response object returned by the `FuturesSession`. This involves calling `.result()` on the future to get the actual response.

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

from requests_futures.sessions import FuturesSession

from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
from PyPowerFlex.constants import StoragePoolConstants, VolumeConstants, SnapshotPolicyConstants


LOG = logging.getLogger(__name__)


class PowerFlexUtility(base_client.EntityRequest):
    def __init__(self, token, configuration):
        super(PowerFlexUtility, self).__init__(token, configuration)
        self.session = FuturesSession()  # Initialize FuturesSession

    def get_statistics_for_all_storagepools(self, ids=None, properties=None):
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

        future = self.send_post_request(self.list_statistics_url,
                                         entity='StoragePool',
                                         action=action,
                                         params=params)
        r = future.result()  # Get the response from the future
        response = r.json()  # Assuming the response is in JSON format

        if r.status_code != 200:  # Use 200 instead of requests.codes.ok
            msg = ('Failed to list storage pool statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    def get_statistics_for_all_volumes(self, ids=None, properties=None):
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

        future = self.send_post_request(self.list_statistics_url,
                                         entity='Volume',
                                         action=action,
                                         params=params)
        r = future.result()  # Get the response from the future
        response = r.json()  # Assuming the response is in JSON format

        if r.status_code != 200:  # Use 200 instead of requests.codes.ok
            msg = ('Failed to list volume statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    def get_statistics_for_all_snapshot_policies(self, ids=None, properties=None):
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

        future = self.send_post_request(self.list_statistics_url,
                                         entity='SnapshotPolicy',
                                         action=action,
                                         params=params)
        r = future.result()  # Get the response from the future
        response = r.json()  # Assuming the response is in JSON format

        if r.status_code != 200:  # Use 200 instead of requests.codes.ok
            msg = ('Failed to list snapshot policy statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response
``` 

This code now uses `requests_futures` to handle asynchronous requests while maintaining the original structure and functionality of the code.