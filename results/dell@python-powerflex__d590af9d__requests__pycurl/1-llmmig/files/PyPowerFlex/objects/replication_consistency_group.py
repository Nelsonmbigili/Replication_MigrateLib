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
import pycurl
from io import BytesIO
import json

from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex.constants import RCGConstants


LOG = logging.getLogger(__name__)


class ReplicationConsistencyGroup(base_client.EntityRequest):
    def create_snapshot(self,
                       rcg_id):
        """Create a snapshot of PowerFlex replication consistency group.

        :param rcg_id: str
        :return: dict
        """

        action = 'createReplicationConsistencyGroupSnapshots'

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=rcg_id)
        if r != 200:  # HTTP status code for OK
            msg = ('Failed to create a snapshot of PowerFlex {entity} '
                   'with id {_id} . Error: {response}'.format(entity=self.entity,
                                                      _id=rcg_id,
                                                      response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=rcg_id)

    def send_post_request(self, url, action, entity, entity_id=None, params=None):
        """Send a POST request using pycurl.

        :param url: str
        :param action: str
        :param entity: str
        :param entity_id: str
        :param params: dict
        :return: tuple (HTTP status code, response content)
        """
        # Prepare the full URL
        full_url = f"{url}/{entity}/{entity_id}/action/{action}" if entity_id else f"{url}/{entity}/action/{action}"

        # Prepare the POST data
        post_data = json.dumps(params) if params else ""

        # Initialize pycurl
        curl = pycurl.Curl()
        response_buffer = BytesIO()

        try:
            # Set pycurl options
            curl.setopt(pycurl.URL, full_url)
            curl.setopt(pycurl.POST, 1)
            curl.setopt(pycurl.POSTFIELDS, post_data)
            curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
            curl.setopt(pycurl.HTTPHEADER, [
                'Content-Type: application/json',
                'Accept: application/json'
            ])

            # Perform the request
            curl.perform()

            # Get the HTTP status code
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)

        finally:
            # Clean up the curl object
            curl.close()

        # Decode the response
        response_content = response_buffer.getvalue().decode('utf-8')
        response_buffer.close()

        return status_code, response_content

    def get_statistics(self, rcg_id):
        """Get related PowerFlex Statistics for RCG.

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

    # Other methods remain unchanged
