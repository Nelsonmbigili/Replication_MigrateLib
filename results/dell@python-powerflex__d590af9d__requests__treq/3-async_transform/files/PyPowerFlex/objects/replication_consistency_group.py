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
from PyPowerFlex.constants import RCGConstants


LOG = logging.getLogger(__name__)


class ReplicationConsistencyGroup(base_client.EntityRequest):
    async def create_snapshot(self, rcg_id):
        """Create a snapshot of PowerFlex replication consistency group.

        :param rcg_id: str
        :return: dict
        """

        action = 'createReplicationConsistencyGroupSnapshots'

        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=rcg_id)
        if r.code != 200:  # Equivalent to requests.codes.ok
            msg = ('Failed to create a snapshot of PowerFlex {entity} '
                   'with id {_id} . Error: {response}'.format(entity=self.entity,
                                                              _id=rcg_id,
                                                              response=await response.text()))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=rcg_id)

    async def get_all_statistics(self, api_version_less_than_3_6):
        """List statistics of all replication consistency groups for PowerFlex.
        :param api_version_less_than_3_6: bool
        :return: dict
        """
        params = {'properties': RCGConstants.DEFAULT_STATISTICS_PROPERTIES}
        if not api_version_less_than_3_6:
            params = {'properties': RCGConstants.DEFAULT_STATISTICS_PROPERTIES_ABOVE_3_5}
        params['allIds'] = ""

        r, response = await self.send_post_request(self.list_statistics_url,
                                                   entity=self.entity,
                                                   action="querySelectedStatistics",
                                                   params=params)
        if r.code != 200:  # Equivalent to requests.codes.ok
            msg = ('Failed to list replication consistency group statistics for PowerFlex. '
                   'Error: {response}'.format(response=await response.text()))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await response.json()

    async def query_selected_statistics(self, properties, ids=None):
        """Query PowerFlex replication consistency group statistics.

        :type properties: list
        :type ids: list of replication consistency group IDs or None for all
                   replication consistency groups
        :rtype: dict
        """

        action = "querySelectedStatistics"

        params = dict(properties=properties)

        if ids:
            params["ids"] = ids
        else:
            params["allIds"] = ""

        return await self._query_selected_statistics(action, params)
