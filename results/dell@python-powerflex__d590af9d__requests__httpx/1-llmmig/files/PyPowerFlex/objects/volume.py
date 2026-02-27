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
    def add_mapped_sdc(self,
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

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=volume_id,
                                             params=params)
        if r.status_code != httpx.codes.OK:  # Replaced requests.codes.ok with httpx.codes.OK
            msg = ('Failed to map PowerFlex {entity} with id {_id} '
                   'to SDC. Error: {response}'.format(entity=self.entity,
                                                      _id=volume_id,
                                                      response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=volume_id)

    def create(self,
               storage_pool_id,
               size_in_gb,
               name=None,
               volume_type=None,
               use_rmcache=None,
               compression_method=None):
        """Create PowerFlex volume.

        :param storage_pool_id: str
        :param size_in_gb: int
        :param name: str
        :param volume_type: one of predefined attributes of VolumeType
        :type volume_type: str
        :param use_rmcache: bool
        :param compression_method: one of predefined attributes of
                                   CompressionMethod
        :type compression_method: str
        :return: dict
        """

        params = dict(
            storagePoolId=storage_pool_id,
            volumeSizeInGb=size_in_gb,
            name=name,
            volumeType=volume_type,
            useRmcache=use_rmcache,
            compressionMethod=compression_method
        )

        return self._create_entity(params)

    def delete(self, volume_id, remove_mode, allow_ext_managed=None):
        """Remove PowerFlex volume.

        :param volume_id: str
        :param remove_mode: one of predefined attributes of RemoveMode
        :param allow_ext_managed: bool
        :return: None
        """

        params = dict(
            removeMode=remove_mode,
            allowOnExtManagedVol=allow_ext_managed
        )

        return self._delete_entity(volume_id, params)

    def extend(self, volume_id, size_in_gb, allow_ext_managed=None):
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

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=volume_id,
                                             params=params)
        if r.status_code != httpx.codes.OK:  # Replaced requests.codes.ok with httpx.codes.OK
            msg = ('Failed to extend PowerFlex {entity} with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=volume_id,
                                              response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=volume_id)

    # The rest of the methods remain unchanged except for replacing
    # `requests.codes.ok` with `httpx.codes.OK` where applicable.
