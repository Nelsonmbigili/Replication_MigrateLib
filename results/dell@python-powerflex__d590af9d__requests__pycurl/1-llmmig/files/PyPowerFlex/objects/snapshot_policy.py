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
import pycurl
from io import BytesIO

from PyPowerFlex import base_client
from PyPowerFlex import exceptions


LOG = logging.getLogger(__name__)


class AutoSnapshotRemovalAction:
    """Auto snapshot deletion strategy."""

    detach = 'Detach'
    remove = 'Remove'


class SnapshotPolicy(base_client.EntityRequest):
    def _send_post_request(self, url, action, entity, entity_id, params=None):
        """Helper method to send POST requests using pycurl."""
        curl = pycurl.Curl()
        response_buffer = BytesIO()
        headers = [
            'Content-Type: application/json',
            'Accept: application/json'
        ]

        # Construct the full URL
        full_url = f"{url}/{entity}/{entity_id}/{action}"

        # Set up the pycurl request
        curl.setopt(pycurl.URL, full_url)
        curl.setopt(pycurl.POST, 1)
        if params:
            import json
            curl.setopt(pycurl.POSTFIELDS, json.dumps(params))
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)

        # Perform the request
        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            curl.close()
            raise exceptions.PowerFlexClientException(f"pycurl error: {e}")

        # Close the curl object
        curl.close()

        # Get the response body
        response_body = response_buffer.getvalue().decode('utf-8')

        return status_code, response_body

    def add_source_volume(self, snapshot_policy_id, volume_id):
        """Add source volume to PowerFlex snapshot policy.

        :type snapshot_policy_id: str
        :type volume_id: str
        :rtype: dict
        """

        action = 'addSourceVolumeToSnapshotPolicy'

        params = dict(
            sourceVolumeId=volume_id
        )

        status_code, response = self._send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=snapshot_policy_id,
                                                        params=params)
        if status_code != 200:
            msg = ('Failed to add source volume to PowerFlex {entity} '
                   'with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=snapshot_policy_id,
                                              response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=snapshot_policy_id)

    def modify(self,
               snapshot_policy_id,
               auto_snap_creation_cadence_in_min,
               retained_snaps_per_level):
        """Modify PowerFlex snapshot policy.

        :type snapshot_policy_id: str
        :type auto_snap_creation_cadence_in_min: int
        :type retained_snaps_per_level: list[int]
        :rtype: dict
        """

        action = 'modifySnapshotPolicy'

        params = dict(
            autoSnapshotCreationCadenceInMin=auto_snap_creation_cadence_in_min,
            numOfRetainedSnapshotsPerLevel=retained_snaps_per_level
        )

        status_code, response = self._send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=snapshot_policy_id,
                                                        params=params)
        if status_code != 200:
            msg = ('Failed to modify PowerFlex {entity} '
                   'with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=snapshot_policy_id,
                                              response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=snapshot_policy_id)

    def pause(self, snapshot_policy_id):
        """Pause PowerFlex snapshot policy.

        :type snapshot_policy_id: str
        :rtype: dict
        """

        action = 'pauseSnapshotPolicy'

        status_code, response = self._send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=snapshot_policy_id)
        if status_code != 200:
            msg = ('Failed to pause PowerFlex {entity} with id {_id}.'
                   ' Error: {response}'.format(entity=self.entity,
                                               _id=snapshot_policy_id,
                                               response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=snapshot_policy_id)

    def remove_source_volume(self,
                             snapshot_policy_id,
                             volume_id,
                             auto_snap_removal_action,
                             detach_locked_auto_snaps=None):
        """Remove source volume from PowerFlex snapshot policy.

        :type snapshot_policy_id: str
        :type volume_id: str
        :param auto_snap_removal_action: one of predefined attributes of
                                         AutoSnapshotRemovalAction
        :type auto_snap_removal_action: str
        :type detach_locked_auto_snaps: bool
        :rtype: dict
        """

        action = 'removeSourceVolumeFromSnapshotPolicy'

        params = dict(
            sourceVolumeId=volume_id,
            autoSnapshotRemovalAction=auto_snap_removal_action,
            detachLockedAutoSnapshots=detach_locked_auto_snaps
        )

        status_code, response = self._send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=snapshot_policy_id,
                                                        params=params)
        if status_code != 200:
            msg = ('Failed to remove source volume from PowerFlex {entity} '
                   'with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=snapshot_policy_id,
                                              response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=snapshot_policy_id)
