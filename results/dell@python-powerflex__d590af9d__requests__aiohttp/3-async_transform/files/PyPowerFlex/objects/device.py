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
# See the License for the specific language governing permissions and limitations
# under the License.

import logging

import aiohttp

from PyPowerFlex import base_client
from PyPowerFlex import exceptions


LOG = logging.getLogger(__name__)


class MediaType:
    """Device media types."""

    hdd = 'HDD'
    ssd = 'SSD'
    nvdimm = 'NVDIMM'


class ExternalAccelerationType:
    """Device external acceleration types."""

    invalid = 'Invalid'
    none = 'None'
    read = 'Read'
    write = 'Write'
    read_and_write = 'ReadAndWrite'


class Device(base_client.EntityRequest):
    async def create(self,
                     current_pathname,
                     sds_id,
                     acceleration_pool_id=None,
                     external_acceleration_type=None,
                     force=None,
                     media_type=None,
                     name=None,
                     storage_pool_id=None):
        """Create PowerFlex device.

        :type current_pathname: str
        :type sds_id: str
        :type acceleration_pool_id: str
        :param external_acceleration_type: one of predefined attributes of
                                           ExternalAccelerationType
        :type external_acceleration_type: str
        :type force: bool
        :param media_type: one of predefined attributes of MediaType
        :type media_type: str
        :type name: str
        :type storage_pool_id: str
        :rtype: dict
        """

        if (
                all([storage_pool_id, acceleration_pool_id]) or
                not any([storage_pool_id, acceleration_pool_id])
        ):
            msg = 'Either storage_pool_id or acceleration_pool_id must be ' \
                  'set.'
            raise exceptions.InvalidInput(msg)

        params = dict(
            deviceCurrentPathname=current_pathname,
            sdsId=sds_id,
            accelerationPoolId=acceleration_pool_id,
            externalAccelerationType=external_acceleration_type,
            forceDeviceTakeover=force,
            mediaType=media_type,
            name=name,
            storagePoolId=storage_pool_id
        )

        return await self._create_entity(params)

    async def delete(self, device_id, force=None):
        """Remove PowerFlex device.

        :type device_id: str
        :type force: bool
        :rtype: None
        """

        params = dict(
            forceRemove=force
        )

        return await self._delete_entity(device_id, params)

    async def rename(self, device_id, name):
        """Rename PowerFlex device.

        :type device_id: str
        :type name: str
        :rtype: dict
        """

        action = 'setDeviceName'

        params = dict(
            newName=name
        )

        return await self._rename_entity(action, device_id, params)

    async def set_media_type(self,
                             device_id,
                             media_type):
        """Set PowerFlex device media type.

        :type device_id: str
        :param media_type: one of predefined attributes of MediaType
        :type media_type: str
        :rtype: dict
        """

        action = 'setMediaType'

        params = dict(
            mediaType=media_type
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_action_url, json={
                "action": action,
                "entity": self.entity,
                "entityId": device_id,
                "params": params
            }) as response:
                if response.status != 200:
                    response_text = await response.text()
                    msg = ('Failed to set media type for PowerFlex {entity} '
                           'with id {_id}. Error: {response}'
                           .format(entity=self.entity, _id=device_id,
                                   response=response_text))
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=device_id)

    async def query_selected_statistics(self, properties, ids=None):
        """Query PowerFlex device statistics.

        :type properties: list
        :type ids: list of device IDs or None for all devices
        :rtype: dict
        """

        action = "querySelectedStatistics"

        params = dict(properties=properties)

        if ids:
            params["ids"] = ids
        else:
            params["allIds"] = ""

        return await self._query_selected_statistics(action, params)
