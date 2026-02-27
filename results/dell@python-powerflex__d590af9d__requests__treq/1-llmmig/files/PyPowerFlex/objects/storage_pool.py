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

        response = await self.send_post_request(self.base_action_url,
                                                action=action,
                                                entity=self.entity,
                                                entity_id=storage_pool_id,
                                                params=params)
        if response.code != 200:
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

        response = await self.send_post_request(self.base_action_url,
                                                action=action,
                                                entity=self.entity,
                                                entity_id=storage_pool_id,
                                                params=params)
        if response.code != 200:
            response_text = await response.text()
            msg = (f'Failed to set compression method for PowerFlex {self.entity} '
                   f'with id {storage_pool_id}. Error: {response_text}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=storage_pool_id)

    async def send_post_request(self, url, action, entity, entity_id, params=None):
        """Send a POST request using treq.

        :type url: str
        :type action: str
        :type entity: str
        :type entity_id: str
        :type params: dict
        :rtype: treq response
        """
        full_url = f"{url}/{action}/{entity}/{entity_id}"
        headers = {'Content-Type': 'application/json'}
        try:
            response = await treq.post(full_url, json=params, headers=headers)
            return response
        except Exception as e:
            msg = f"Failed to send POST request to {full_url}. Error: {str(e)}"
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

    async def get(self, entity_id):
        """Get entity details.

        :type entity_id: str
        :rtype: dict
        """
        url = f"{self.base_action_url}/{self.entity}/{entity_id}"
        try:
            response = await treq.get(url)
            if response.code != 200:
                response_text = await response.text()
                msg = f"Failed to get entity with id {entity_id}. Error: {response_text}"
                LOG.error(msg)
                raise exceptions.PowerFlexClientException(msg)
            return await response.json()
        except Exception as e:
            msg = f"Failed to get entity with id {entity_id}. Error: {str(e)}"
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
