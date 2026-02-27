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
import pycurl
from io import BytesIO
import json

from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
from PyPowerFlex.constants import StoragePoolConstants, VolumeConstants, SnapshotPolicyConstants


LOG = logging.getLogger(__name__)


class PowerFlexUtility(base_client.EntityRequest):
    def __init__(self, token, configuration):
        super(PowerFlexUtility, self).__init__(token, configuration)

    def send_post_request(self, url, entity, action, params):
        """Send a POST request using pycurl.

        :param url: str
        :param entity: str
        :param action: str
        :param params: dict
        :return: tuple (HTTP response code, response content)
        """
        buffer = BytesIO()
        curl = pycurl.Curl()

        try:
            # Set up the pycurl request
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.HTTPHEADER, [
                'Content-Type: application/json',
                f'Authorization: Bearer {self.token}'
            ])
            curl.setopt(pycurl.POST, 1)
            curl.setopt(pycurl.POSTFIELDS, json.dumps({
                'entity': entity,
                'action': action,
                'params': params
            }))
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

            # Perform the request
            curl.perform()

            # Get the HTTP response code
            http_code = curl.getinfo(pycurl.RESPONSE_CODE)

        finally:
            curl.close()

        # Decode the response
        response = buffer.getvalue().decode('utf-8')
        return http_code, response

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

        http_code, response = self.send_post_request(self.list_statistics_url,
                                                     entity='StoragePool',
                                                     action=action,
                                                     params=params)
        if http_code != 200:
            msg = ('Failed to list storage pool statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return json.loads(response)

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

        http_code, response = self.send_post_request(self.list_statistics_url,
                                                     entity='Volume',
                                                     action=action,
                                                     params=params)
        if http_code != 200:
            msg = ('Failed to list volume statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return json.loads(response)

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

        http_code, response = self.send_post_request(self.list_statistics_url,
                                                     entity='SnapshotPolicy',
                                                     action=action,
                                                     params=params)
        if http_code != 200:
            msg = ('Failed to list snapshot policy statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return json.loads(response)
