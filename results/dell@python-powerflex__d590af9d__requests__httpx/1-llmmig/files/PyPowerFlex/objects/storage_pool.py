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

import httpx  # Replaced requests with httpx

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
    def create(self,
               media_type,
               protection_domain_id,
               checksum_enabled=None,
               compression_method=None,
               data_layout=None,
               external_acceleration_type=None,
               fgl_accp_id=None,
               name=None,
               rmcache_write_handling_mode=None,
               spare_percentage=None,
               use_rfcache=None,
               use_rmcache=None,
               zero_padding_enabled=None):
        """Create PowerFlex storage pool.

        :param media_type: one of predefined attributes of MediaType
        :type media_type: str
        :type protection_domain_id: str
        :type checksum_enabled: bool
        :param compression_method: one of predefined attributes of
                                   CompressionMethod
        :type compression_method: str
        :param data_layout: one of predefined attributes of DataLayout
        :type data_layout: str
        :param external_acceleration_type: one of predefined attributes of
                                           ExternalAccelerationType
        :type external_acceleration_type: str
        :type fgl_accp_id: str
        :type name: str
        :param rmcache_write_handling_mode: one of predefined attributes of
                                            RmcacheWriteHandlingMode
        :type spare_percentage: int
        :type use_rfcache: bool
        :type use_rmcache: bool
        :type zero_padding_enabled: bool
        :rtype: dict
        """

        if data_layout == DataLayout.fine and not fgl_accp_id:
            msg = 'fgl_accp_id must be set for Fine Granular Storage Pool.'
            raise exceptions.InvalidInput(msg)
        params = dict(
            mediaType=media_type,
            protectionDomainId=protection_domain_id,
            checksumEnabled=checksum_enabled,
            compressionMethod=compression_method,
            dataLayout=data_layout,
            externalAccelerationType=external_acceleration_type,
            fglAccpId=fgl_accp_id,
            name=name,
            rmcacheWriteHandlingMode=rmcache_write_handling_mode,
            sparePercentage=spare_percentage,
            useRfcache=use_rfcache,
            useRmcache=use_rmcache,
            zeroPaddingEnabled=zero_padding_enabled
        )

        return self._create_entity(params)

    def set_checksum_enabled(self, storage_pool_id, checksum_enabled):
        """Enable/disable checksum for PowerFlex storage pool.

        :type storage_pool_id: str
        :type checksum_enabled: bool
        :rtype: dict
        """

        action = 'setChecksumEnabled'

        params = dict(
            checksumEnabled=checksum_enabled
        )

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=storage_pool_id,
                                             params=params)
        if r.status_code != httpx.codes.OK:  # Updated to httpx.codes.OK
            msg = (f'Failed to enable/disable checksum for PowerFlex {self.entity} '
                   f'with id {storage_pool_id}. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=storage_pool_id)

    def set_compression_method(self, storage_pool_id, compression_method):
        """Set compression method for PowerFlex storage pool.

        :type storage_pool_id: str
        :type compression_method: str
        :rtype: dict
        """

        action = 'modifyCompressionMethod'

        params = dict(
            compressionMethod=compression_method
        )

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=storage_pool_id,
                                             params=params)
        if r.status_code != httpx.codes.OK:  # Updated to httpx.codes.OK
            msg = (f'Failed to set compression method for PowerFlex {self.entity} '
                   f'with id {storage_pool_id}. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=storage_pool_id)

    # Other methods remain unchanged except for replacing `requests.codes.ok` with `httpx.codes.OK`
