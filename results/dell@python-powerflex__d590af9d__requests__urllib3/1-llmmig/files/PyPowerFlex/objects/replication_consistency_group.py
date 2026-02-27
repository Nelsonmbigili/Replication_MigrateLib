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

import urllib3

from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex.constants import RCGConstants


LOG = logging.getLogger(__name__)


class ReplicationConsistencyGroup(base_client.EntityRequest):
    def __init__(self):
        super().__init__()
        self.http = urllib3.PoolManager()

    def create_snapshot(self,
                        rcg_id):
        """Create a snapshot of PowerFlex replication consistency group.

        :param rcg_id: str
        :return: dict
        """

        action = 'createReplicationConsistencyGroupSnapshots'

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=rcg_id)
        if r.status != 200:  # Replaced requests.codes.ok with 200
            msg = ('Failed to create a snapshot of PowerFlex {entity} '
                   'with id {_id} . Error: {response}'.format(entity=self.entity,
                                                              _id=rcg_id,
                                                              response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=rcg_id)

    def get_all_statistics(self, api_version_less_than_3_6):
        """list statistics of all replication consistency groups for PowerFlex.
        :param api_version_less_than_3_6: bool
        :return: dict
        """
        params = {'properties': RCGConstants.DEFAULT_STATISTICS_PROPERTIES}
        if not api_version_less_than_3_6:
            params = {'properties': RCGConstants.DEFAULT_STATISTICS_PROPERTIES_ABOVE_3_5}
        params['allIds'] = ""

        r, response = self.send_post_request(self.list_statistics_url,
                                             entity=self.entity,
                                             action="querySelectedStatistics",
                                             params=params)
        if r.status != 200:  # Replaced requests.codes.ok with 200
            msg = ('Failed to list replication consistencty group statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    def send_post_request(self, url, action, entity, entity_id=None, params=None):
        """Send a POST request using urllib3.

        :param url: str
        :param action: str
        :param entity: str
        :param entity_id: str
        :param params: dict
        :return: tuple (HTTPResponse, dict)
        """
        full_url = f"{url}/{action}"
        if entity_id:
            full_url = f"{full_url}/{entity_id}"

        headers = {
            'Content-Type': 'application/json'
        }

        body = None
        if params:
            import json
            body = json.dumps(params)

        response = self.http.request(
            "POST",
            full_url,
            headers=headers,
            body=body
        )

        # Decode the response body
        response_data = response.data.decode('utf-8')

        return response, response_data
