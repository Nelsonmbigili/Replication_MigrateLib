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

LOG = logging.getLogger(__name__)


class CompressionMethod:
    """Volume compression methods."""

    invalid = 'Invalid'
    none = 'None'
    normal = 'Normal'


class RemoveMode:
    """Volume remove modes.

    Represents volume deletion strategy. See PowerFlex documentation for more
    information.
    """

    only_me = 'ONLY_ME'
    including_descendants = 'INCLUDING_DESCENDANTS'
    descendants_only = 'DESCENDANTS_ONLY'
    whole_vtree = 'WHOLE_VTREE'


class VolumeType:
    """Volume provisioning types."""

    thick = 'ThickProvisioned'
    thin = 'ThinProvisioned'


class Volume(base_client.EntityRequest):
    async def add_mapped_sdc(self,
                             volume_id,
                             sdc_id=None,
                             sdc_guid=None,
                             allow_multiple_mappings=None,
                             allow_ext_managed=None,
                             access_mode=None):
        """Map PowerFlex volume to SDC.

        :param volume_id: str
        :param sdc_id: str
        :param sdc_guid: str
        :param allow_multiple_mappings: bool
        :param allow_ext_managed: bool
        :type access_mode: str
        :return: dict
        """

        action = 'addMappedSdc'

        if all([sdc_id, sdc_guid]) or not any([sdc_id, sdc_guid]):
            msg = 'Either sdc_id or sdc_guid must be set.'
            raise exceptions.InvalidInput(msg)
        params = dict(
            sdcId=sdc_id,
            guid=sdc_guid,
            allowMultipleMappings=allow_multiple_mappings,
            allowOnExtManagedVol=allow_ext_managed,
            accessMode=access_mode
        )

        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=volume_id,
                                                   params=params)
        if r.code != 200:  # treq uses response.code for status codes
            msg = ('Failed to map PowerFlex {entity} with id {_id} '
                   'to SDC. Error: {response}'.format(entity=self.entity,
                                                      _id=volume_id,
                                                      response=await response.text()))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=volume_id)

    async def extend(self, volume_id, size_in_gb, allow_ext_managed=None):
        """Extend PowerFlex volume.

        :param volume_id: str
        :param size_in_gb: int
        :param allow_ext_managed: bool
        :return: dict
        """

        action = 'setVolumeSize'

        params = dict(
            sizeInGB=size_in_gb,
            allowOnExtManagedVol=allow_ext_managed
        )

        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=volume_id,
                                                   params=params)
        if r.code != 200:
            msg = ('Failed to extend PowerFlex {entity} with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=volume_id,
                                              response=await response.text()))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=volume_id)

    async def lock_auto_snapshot(self, volume_id):
        """Lock auto snapshot of PowerFlex volume.

        :param volume_id: str
        :return: dict
        """

        action = 'lockAutoSnapshot'

        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=volume_id)
        if r.code != 200:
            msg = ('Failed to lock AutoSnapshot for PowerFlex {entity} '
                   'with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=volume_id,
                                              response=await response.text()))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=volume_id)

    async def unlock_auto_snapshot(self, volume_id, remove_auto_snapshot=None):
        """Unlock auto snapshot of PowerFlex volume.

        :param volume_id: str
        :param remove_auto_snapshot: bool
        :return: dict
        """

        action = 'unlockAutoSnapshot'

        params = dict(
            autoSnapshotWillBeRemoved=remove_auto_snapshot
        )

        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=volume_id,
                                                   params=params)
        if r.code != 200:
            msg = ('Failed to unlock AutoSnapshot for PowerFlex {entity} '
                   'with id {_id}. Error: '
                   '{response}'.format(entity=self.entity, _id=volume_id,
                                       response=await response.text()))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=volume_id)

    async def set_compression_method(self, volume_id, compression_method):
        """
        Modify the compression method to be used for a Volume, relevant only
        if the volume has a space efficient data layout.

        :param volume_id: ID of the volume
        :type volume_id: str
        :param compression_method: one of predefined attributes of
        CompressionMethod
        :type compression_method: str
        :return: dict
        """

        action = 'modifyCompressionMethod'

        params = dict(
            compressionMethod=compression_method,
        )

        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=volume_id,
                                                   params=params)
        if r.code != 200:
            msg = ('Failed to update the compression method of PowerFlex'
                   ' {entity} with id'
                   ' {_id}. Error: {response}'.format(entity=self.entity,
                                                      _id=volume_id,
                                                      response=await response.text()))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=volume_id)
