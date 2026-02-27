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
import aiohttp  # Replaced requests with aiohttp
from PyPowerFlex import base_client
from PyPowerFlex import exceptions


LOG = logging.getLogger(__name__)


class Sdc(base_client.EntityRequest):
    async def delete(self, sdc_id):
        """Remove PowerFlex SDC.

        :type sdc_id: str
        :rtype: None
        """

        return await self._delete_entity(sdc_id)  # Added await for async call

    async def get_mapped_volumes(self, sdc_id, filter_fields=None, fields=None):
        """Get PowerFlex volumes mapped to SDC.

        :type sdc_id: str
        :type filter_fields: dict
        :type fields: list|tuple
        :rtype: list[dict]
        """

        return await self.get_related(sdc_id, 'Volume', filter_fields, fields)  # Added await

    async def rename(self, sdc_id, name):
        """Rename PowerFlex SDC.

        :type sdc_id: str
        :type name: str
        :rtype: dict
        """

        action = 'setSdcName'

        params = dict(
            sdcName=name
        )

        return await self._rename_entity(action, sdc_id, params)  # Added await

    async def set_performance_profile(self, sdc_id, perf_profile):
        """Apply a performance profile to the specified SDC.

        :type sdc_id: str
        :type perf_profile: str
        :rtype: dict
        """

        action = 'setSdcPerformanceParameters'

        params = dict(
            perfProfile=perf_profile
        )
        return await self._perform_entity_operation_based_on_action(  # Added await
            sdc_id, action, params=params, add_entity=False
        )

    async def query_selected_statistics(self, properties, ids=None):
        """Query PowerFlex SDC statistics.

        :type properties: list
        :type ids: list of SDC IDs or None for all SDC
        :rtype: dict
        """

        action = "querySelectedStatistics"

        params = dict(properties=properties)

        if ids:
            params["ids"] = ids
        else:
            params["allIds"] = ""

        return await self._query_selected_statistics(action, params)  # Added await
