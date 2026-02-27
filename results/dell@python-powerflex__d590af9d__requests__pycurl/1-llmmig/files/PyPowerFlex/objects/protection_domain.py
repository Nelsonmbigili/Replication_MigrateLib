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
import io
import json

from PyPowerFlex import base_client
from PyPowerFlex import exceptions


LOG = logging.getLogger(__name__)


class RFCacheOperationMode:
    """RFcache operation mode."""

    none = 'None'
    read = 'Read'
    write = 'Write'
    read_and_write = 'ReadAndWrite'
    write_miss = 'WriteMiss'


class ProtectionDomain(base_client.EntityRequest):
    def _send_post_request(self, url, action, entity, entity_id, params=None):
        """
        Helper method to send a POST request using pycurl.

        :type url: str
        :type action: str
        :type entity: str
        :type entity_id: str
        :type params: dict
        :rtype: tuple (HTTP status code, response content)
        """
        buffer = io.BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.setopt(c.POST, 1)

        # Prepare the POST data
        post_data = {
            "action": action,
            "entity": entity,
            "entityId": entity_id
        }
        if params:
            post_data.update(params)

        c.setopt(c.POSTFIELDS, json.dumps(post_data))
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])

        try:
            c.perform()
            status_code = c.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            LOG.error(f"pycurl error: {e}")
            raise exceptions.PowerFlexClientException(f"pycurl error: {e}")
        finally:
            c.close()

        response = buffer.getvalue().decode('utf-8')
        return status_code, response

    def activate(self, protection_domain_id, force=False):
        """Activate PowerFlex protection domain.

        :type protection_domain_id: str
        :type force: bool
        :rtype: dict
        """

        action = 'activateProtectionDomain'

        params = dict(
            forceActivate=force
        )

        status_code, response = self._send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=protection_domain_id,
                                                        params=params)
        if status_code != 200:
            msg = ('Failed to activate PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=protection_domain_id,
                           response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=protection_domain_id)

    def inactivate(self, protection_domain_id, force=False):
        """Inactivate PowerFlex protection domain.

        :type protection_domain_id: str
        :type force: bool
        :rtype: dict
        """

        action = 'inactivateProtectionDomain'

        params = dict(
            forceShutdown=force
        )

        status_code, response = self._send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=protection_domain_id,
                                                        params=params)
        if status_code != 200:
            msg = ('Failed to inactivate PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=protection_domain_id,
                           response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=protection_domain_id)

    def network_limits(self, protection_domain_id, rebuild_limit=None,
                       rebalance_limit=None, vtree_migration_limit=None,
                       overall_limit=None):
        """
        Setting the Network limits of the protection domain.

        :type protection_domain_id: str
        :type rebuild_limit: int
        :type rebalance_limit: int
        :type vtree_migration_limit: int
        :type overall_limit: int
        :rtype dict
        """

        action = "setSdsNetworkLimits"

        params = dict(
            rebuildLimitInKbps=rebuild_limit,
            rebalanceLimitInKbps=rebalance_limit,
            vtreeMigrationLimitInKbps=vtree_migration_limit,
            overallLimitInKbps=overall_limit
        )
        status_code, response = self._send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=protection_domain_id,
                                                        params=params)

        if status_code != 200:
            msg = ('Failed to update the network limits of PowerFlex {entity}'
                   ' with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=protection_domain_id,
                           response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=protection_domain_id)

    def set_rfcache_enabled(self, protection_domain_id, enable_rfcache=None):
        """
        Enable/Disable the RFcache in the Protection Domain.

        :type protection_domain_id: str
        :type enable_rfcache: bool
        :rtype dict
        """

        action = "disableSdsRfcache"
        if enable_rfcache:
            action = "enableSdsRfcache"

        status_code, response = self._send_post_request(self.base_action_url,
                                                        action=action,
                                                        entity=self.entity,
                                                        entity_id=protection_domain_id)
        if status_code != 200:
            msg = ('Failed to enable/disable RFcache in PowerFlex {entity} '
                   ' with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=protection_domain_id,
                           response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=protection_domain_id)
