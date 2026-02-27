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

        :type rcg_id: str
        :rtype: dict
        """

        return self.get_related(rcg_id,
                                'Statistics')

    def create(self,
               rpo,
               protection_domain_id,
               remote_protection_domain_id=None,
               peer_mdm_id=None,
               destination_system_id=None,
               name=None,
               force_ignore_consistency=None,
               activity_mode=None):
        """Create PowerFlex RCG.

        :param rpo: int
        :param protection_domain_id: str
        :param remote_protection_domain_id: str
        :param peer_mdm_id: str
        :type destination_system_id: str
        :param name: str
        :param force_ignore_consistency: bool
        :type activity_mode: str
        :return: dict
        """

        params = dict(
            rpoInSeconds=rpo,
            protectionDomainId=protection_domain_id,
            remoteProtectionDomainId=remote_protection_domain_id,
            peerMdmId=peer_mdm_id,
            destinationSystemId=destination_system_id,
            name=name,
            forceIgnoreConsistency=force_ignore_consistency,
            activityMode=activity_mode
        )

        return self._create_entity(params)

    def delete(self,
               rcg_id,
               force_ignore_consistency=None):
        """Delete PowerFlex RCG.

        :param rcg_id: str
        :param force_ignore_consistency: bool
        :return: None
        """

        params = dict(
            forceIgnoreConsistency=force_ignore_consistency
        )

        return self._delete_entity(rcg_id, params)

    def activate(self, rcg_id):
        """Activate PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """
        action = "activate%s" % self.entity
        return self._perform_entity_operation_based_on_action\
            (rcg_id, action, add_entity=False)

    def inactivate(self, rcg_id):
        """Inactivate PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """
        action = "terminate%s" % self.entity
        return self._perform_entity_operation_based_on_action\
            (rcg_id, action, add_entity=False)

    def freeze(self, rcg_id):
        """Freeze PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """

        return self._perform_entity_operation_based_on_action(rcg_id, "freezeApply")

    def unfreeze(self, rcg_id):
        """Freeze PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """

        return self._perform_entity_operation_based_on_action(rcg_id, "unfreezeApply")

    def pause(self, rcg_id, pause_mode):
        """Pause PowerFlex RCG.

        :param rcg_id: str
        :param pause_mode: str
        :return: dict
        """

        params = dict(
            pauseMode=pause_mode
        )
        return self._perform_entity_operation_based_on_action(rcg_id, "pause", params)

    def resume(self, rcg_id):
        """Resume PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """

        return self._perform_entity_operation_based_on_action(rcg_id, "resume")

    def failover(self, rcg_id):
        """Failover PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """

        return self._perform_entity_operation_based_on_action(rcg_id, "failover")

    def sync(self, rcg_id):
        """Synchronize PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """

        return self._perform_entity_operation_based_on_action(rcg_id, "syncNow")

    def restore(self, rcg_id):
        """Restore PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """

        return self._perform_entity_operation_based_on_action(rcg_id, "restore")

    def reverse(self, rcg_id):
        """Reverse PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """

        return self._perform_entity_operation_based_on_action(rcg_id, "reverse")

    def switchover(self, rcg_id, force=False):
        """Switch over PowerFlex RCG.

        :param rcg_id: str
        :param force: bool
        :return: dict
        """
        url_params = {
            'force':force
        }
        return self._perform_entity_operation_based_on_action(rcg_id, "switchover", **url_params)

    def set_as_consistent(self, rcg_id):
        """Set PowerFlex RCG as consistent.

        :param rcg_id: str
        :return: dict
        """
        action = "set%sConsistent" % self.entity
        return self._perform_entity_operation_based_on_action\
            (rcg_id, action, add_entity=False)

    def set_as_inconsistent(self, rcg_id):
        """Set PowerFlex RCG as in-consistent.

        :param rcg_id: str
        :return: dict
        """
        action = "set%sInconsistent" % self.entity
        return self._perform_entity_operation_based_on_action\
            (rcg_id, action, add_entity=False)

    def modify_rpo(self, rcg_id, rpo_in_seconds):
        """Modify rpo of PowerFlex RCG.

        :param rcg_id: str
        :param rpo_in_seconds: int
        :return: dict
        """

        params = dict(
            rpoInSeconds=rpo_in_seconds
        )
        action = "Modify%sRpo" % self.entity
        return self._perform_entity_operation_based_on_action\
            (rcg_id, action, params=params, add_entity=False)

    def modify_target_volume_access_mode(self, rcg_id, target_volume_access_mode):
        """Modify TargetVolumeAccessMode of PowerFlex RCG.

        :param rcg_id: str
        :param target_volume_access_mode: str
        :return: dict
        """

        params = dict(
            targetVolumeAccessMode=target_volume_access_mode
        )
        action = "modify%sTargetVolumeAccessMode" % self.entity
        return self._perform_entity_operation_based_on_action\
            (rcg_id, action, params=params, add_entity=False)

    def rename_rcg(self, rcg_id, new_name):
        """Rename PowerFlex RCG.

        :param rcg_id: str
        :param new_name: str
        :return: dict
        """

        params = dict(
            newName=new_name
        )
        return self._perform_entity_operation_based_on_action\
            (rcg_id, "rename", params=params)

    def get_replication_pairs(self, rcg_id):
        """Get replication pairs of PowerFlex RCG.

        :param rcg_id: str
        :return: dict
        """

        return self.get_related(rcg_id,
                                'ReplicationPair')

    def get_all_statistics(self, api_version_less_than_3_6):
        """list statistics of all replication consistency groups for PowerFlex.
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