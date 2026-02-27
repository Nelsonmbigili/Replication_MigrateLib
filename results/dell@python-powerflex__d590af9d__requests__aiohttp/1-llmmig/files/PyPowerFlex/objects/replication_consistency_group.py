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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import aiohttp
import asyncio

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
        if r.status != 200:  # aiohttp uses `status` instead of `status_code`
            msg = ('Failed to create a snapshot of PowerFlex {entity} '
                   'with id {_id} . Error: {response}'.format(entity=self.entity,
                                                              _id=rcg_id,
                                                              response=response))
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
        if r.status != 200:  # aiohttp uses `status` instead of `status_code`
            msg = ('Failed to list replication consistency group statistics for PowerFlex. '
                   'Error: {response}'.format(response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    async def send_post_request(self, url, action, entity, entity_id=None, params=None):
        """Send a POST request using aiohttp.

        :param url: str
        :param action: str
        :param entity: str
        :param entity_id: str
        :param params: dict
        :return: tuple (response, response_content)
        """
        async with aiohttp.ClientSession() as session:
            full_url = f"{url}/{action}"
            if entity_id:
                full_url = f"{full_url}/{entity_id}"

            async with session.post(full_url, json=params) as response:
                response_content = await response.json()
                return response, response_content

    async def get(self, entity_id):
        """Get an entity by ID using aiohttp.

        :param entity_id: str
        :return: dict
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_action_url}/{self.entity}/{entity_id}"
            async with session.get(url) as response:
                if response.status != 200:
                    msg = f"Failed to get entity {self.entity} with id {entity_id}."
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)
                return await response.json()

    async def _delete_entity(self, entity_id, params):
        """Delete an entity using aiohttp.

        :param entity_id: str
        :param params: dict
        :return: None
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_action_url}/{self.entity}/{entity_id}"
            async with session.delete(url, json=params) as response:
                if response.status != 200:
                    msg = f"Failed to delete entity {self.entity} with id {entity_id}."
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)

    async def _perform_entity_operation_based_on_action(self, entity_id, action, params=None, add_entity=True):
        """Perform an entity operation using aiohttp.

        :param entity_id: str
        :param action: str
        :param params: dict
        :param add_entity: bool
        :return: dict
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_action_url}/{self.entity}/{entity_id}/{action}" if add_entity else f"{self.base_action_url}/{action}"
            async with session.post(url, json=params) as response:
                if response.status != 200:
                    msg = f"Failed to perform action {action} on entity {self.entity} with id {entity_id}."
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)
                return await response.json()
