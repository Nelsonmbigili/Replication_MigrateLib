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


LOG = logging.getLogger(__name__)


class FaultSet(base_client.EntityRequest):
    async def clear(self, fault_set_id):
        """Clear PowerFlex fault set.

        :type fault_set_id: str
        :rtype: dict
        """

        action = 'clearFaultSet'

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.base_action_url, json={
                    "action": action,
                    "entity": self.entity,
                    "entityId": fault_set_id
                }) as r:
                    response = await r.text()
                    if r.status != 200:
                        msg = ('Failed to clear PowerFlex {entity} '
                               'with id {_id}. Error: {response}'
                               .format(entity=self.entity, _id=fault_set_id,
                                       response=response))
                        LOG.error(msg)
                        raise exceptions.PowerFlexClientException(msg)

            except aiohttp.ClientError as e:
                msg = f"HTTP request failed: {str(e)}"
                LOG.error(msg)
                raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=fault_set_id)

    async def create(self, protection_domain_id, name=None):
        """Create PowerFlex fault set.

        :type protection_domain_id: str
        :type name: str
        :rtype: dict
        """

        params = dict(
            protectionDomainId=protection_domain_id,
            name=name
        )

        return await self._create_entity(params)

    async def get_sdss(self, fault_set_id, filter_fields=None, fields=None):
        """Get related PowerFlex SDSs for fault set.

        :type fault_set_id: str
        :type filter_fields: dict
        :type fields: list|tuple
        :rtype: list[dict]
        """

        return await self.get_related(fault_set_id,
                                      'Sds',
                                      filter_fields,
                                      fields)

    async def delete(self, fault_set_id):
        """Remove PowerFlex fault set.

        :type fault_set_id: str
        :rtype: None
        """

        return await self._delete_entity(fault_set_id)

    async def rename(self, fault_set_id, name):
        """Rename PowerFlex fault set.

        :type fault_set_id: str
        :type name: str
        :rtype: dict
        """

        action = 'setFaultSetName'

        params = dict(
            newName=name
        )

        return await self._rename_entity(action, fault_set_id, params)

    async def query_selected_statistics(self, properties, ids=None):
        """Query PowerFlex fault set statistics.

        :type properties: list
        :type ids: list of fault set IDs or None for all fault sets
        :rtype: dict
        """

        action = "querySelectedStatistics"

        params = dict(properties=properties)

        if ids:
            params["ids"] = ids
        else:
            params["allIds"] = ""

        return await self._query_selected_statistics(action, params)
