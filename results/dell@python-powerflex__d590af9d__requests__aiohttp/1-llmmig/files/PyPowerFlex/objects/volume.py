import logging
import aiohttp
import asyncio

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
    async def send_post_request(self, url, action, entity, entity_id, params=None):
        """Send a POST request using aiohttp.

        :param url: str
        :param action: str
        :param entity: str
        :param entity_id: str
        :param params: dict
        :return: tuple (response_status, response_body)
        """
        async with aiohttp.ClientSession() as session:
            try:
                full_url = f"{url}/{action}/{entity}/{entity_id}"
                async with session.post(full_url, json=params) as response:
                    response_body = await response.text()
                    return response.status, response_body
            except aiohttp.ClientError as e:
                LOG.error(f"HTTP request failed: {e}")
                raise exceptions.PowerFlexClientException(f"HTTP request failed: {e}")

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

        status, response = await self.send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=volume_id,
                                                        params=params)
        if status != 200:  # HTTP 200 OK
            msg = ('Failed to map PowerFlex {entity} with id {_id} '
                   'to SDC. Error: {response}'.format(entity=self.entity,
                                                      _id=volume_id,
                                                      response=response))
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

        status, response = await self.send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=volume_id,
                                                        params=params)
        if status != 200:  # HTTP 200 OK
            msg = ('Failed to extend PowerFlex {entity} with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=volume_id,
                                              response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=volume_id)

    async def lock_auto_snapshot(self, volume_id):
        """Lock auto snapshot of PowerFlex volume.

        :param volume_id: str
        :return: dict
        """

        action = 'lockAutoSnapshot'

        status, response = await self.send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=volume_id)
        if status != 200:  # HTTP 200 OK
            msg = ('Failed to lock AutoSnapshot for PowerFlex {entity} '
                   'with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=volume_id,
                                              response=response))
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

        status, response = await self.send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=volume_id,
                                                        params=params)
        if status != 200:  # HTTP 200 OK
            msg = ('Failed to unlock AutoSnapshot for PowerFlex {entity} '
                   'with id {_id}. Error: '
                   '{response}'.format(entity=self.entity, _id=volume_id,
                                       response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return await self.get(entity_id=volume_id)
