### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, the following changes were made:

1. **Importing PycURL**: The `requests` library was replaced with `pycurl`. This requires importing the `pycurl` module.
2. **Sending HTTP Requests**: The `send_post_request` method was modified to use `pycurl` for making HTTP POST requests. This involves setting up a `pycurl.Curl` object, configuring it with the necessary options (like URL, POST data, etc.), and executing the request.
3. **Handling Responses**: The response handling was adjusted to read the response data from a `BytesIO` object, as `pycurl` does not return a response object like `requests` does.
4. **Error Handling**: The error handling was updated to check for HTTP response codes using `pycurl`'s methods.

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
import pycurl
from io import BytesIO

from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
from PyPowerFlex.constants import StoragePoolConstants, VolumeConstants, SnapshotPolicyConstants


LOG = logging.getLogger(__name__)


class PowerFlexUtility(base_client.EntityRequest):
    def __init__(self, token, configuration):
        super(PowerFlexUtility, self).__init__(token, configuration)

    def send_post_request(self, url, entity, action, params):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.POST, 1)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        post_fields = '&'.join(f'{key}={value}' for key, value in params.items())
        c.setopt(c.POSTFIELDS, post_fields)
        c.setopt(c.HTTPHEADER, ['Authorization: Bearer ' + self.token])
        
        try:
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            response_data = buffer.getvalue().decode('utf-8')
            return response_code, response_data
        finally:
            c.close()

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

        r, response = self.send_post_request(self.list_statistics_url,
                                             entity='StoragePool',
                                             action=action,
                                             params=params)
        if r != 200:
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

        r, response = self.send_post_request(self.list_statistics_url,
                                             entity='Volume',
                                             action=action,
                                             params=params)
        if r != 200:
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

        r, response = self.send_post_request(self.list_statistics_url,
                                             entity='SnapshotPolicy',
                                             action=action,
                                             params=params)
        if r != 200:
            msg = ('Failed to list snapshot policy statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response
```