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
from PyPowerFlex.objects import Sds


LOG = logging.getLogger(__name__)


class CompressionMethod:
    """Storage pool compression methods."""

    invalid = 'Invalid'
    none = 'None'
    normal = 'Normal'


class DataLayout:
    """Storage pool data layouts."""

    invalid = 'InvalidLayout'
    medium = 'MediumGranularity'
    fine = 'FineGranularity'


class ExternalAccelerationType:
    """Storage pool external acceleration types."""

    none = 'None'
    read = 'Read'
    write = 'Write'
    read_and_write = 'ReadAndWrite'


class MediaType:
    """Storage pool media types."""

    hdd = 'HDD'
    ssd = 'SSD'
    transitional = 'Transitional'


class RmcacheWriteHandlingMode:
    """Rmcache write handling modes."""

    passthrough = 'Passthrough'
    cached = 'Cached'


class StoragePool(base_client.EntityRequest):
    async def set_checksum_enabled(self, storage_pool_id, checksum_enabled):
        """Enable/disable checksum for PowerFlex storage pool.

        :type storage_pool_id: str
        :type checksum_enabled: bool
        :rtype: dict
        """

        action = 'setChecksumEnabled'

        params = dict(
            checksumEnabled=checksum_enabled
        )

        async with aiohttp.ClientSession() as session:  # aiohttp session
            async with session.post(
                self.base_action_url,
                json={
                    "action": action,
                    "entity": self.entity,
                    "entityId": storage_pool_id,
                    "params": params,
                },
            ) as response:
                if response.status != 200:  # aiohttp uses response.status
                    response_text = await response.text()
                    msg = (f'Failed to enable/disable checksum for PowerFlex {self.entity} '
                           f'with id {storage_pool_id}. Error: {response_text}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)

                return await self.get(entity_id=storage_pool_id)

    async def set_compression_method(self, storage_pool_id, compression_method):
        """Set compression method for PowerFlex storage pool.

        :type storage_pool_id: str
        :type compression_method: str
        :rtype: dict
        """

        action = 'modifyCompressionMethod'

        params = dict(
            compressionMethod=compression_method
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_action_url,
                json={
                    "action": action,
                    "entity": self.entity,
                    "entityId": storage_pool_id,
                    "params": params,
                },
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    msg = (f'Failed to set compression method for PowerFlex {self.entity} '
                           f'with id {storage_pool_id}. Error: {response_text}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)

                return await self.get(entity_id=storage_pool_id)

    async def set_external_acceleration_type(
            self,
            storage_pool_id,
            external_acceleration_type,
            override_device_configuration=None,
            keep_device_ext_acceleration=None
    ):
        """Set external acceleration type for PowerFlex storage pool.

        :type storage_pool_id: str
        :param external_acceleration_type: one of predefined attributes of
                                           ExternalAccelerationType
        :type external_acceleration_type: str
        :type override_device_configuration: bool
        :type keep_device_ext_acceleration: bool
        :rtype: dict
        """

        action = 'setExternalAccelerationType'

        if all([override_device_configuration, keep_device_ext_acceleration]):
            msg = ('Either override_device_configuration or '
                   'keep_device_specific_external_acceleration can be set.')
            raise exceptions.InvalidInput(msg)
        params = dict(
            externalAccelerationType=external_acceleration_type,
            overrideDeviceConfiguration=override_device_configuration,
            keepDeviceSpecificExternalAcceleration=keep_device_ext_acceleration
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_action_url,
                json={
                    "action": action,
                    "entity": self.entity,
                    "entityId": storage_pool_id,
                    "params": params,
                },
            ) as response:
                if response.status != 200:
                    response_text = await response.text()
                    msg = (f'Failed to set external acceleration type for PowerFlex '
                           f'{self.entity} with id {storage_pool_id}. Error: {response_text}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)

                return await self.get(entity_id=storage_pool_id)

    # Other methods that use HTTP requests would follow the same pattern:
    # - Use `async def` for the method definition.
    # - Use `aiohttp.ClientSession` for making HTTP requests.
    # - Use `await` to handle asynchronous operations like reading response content.
