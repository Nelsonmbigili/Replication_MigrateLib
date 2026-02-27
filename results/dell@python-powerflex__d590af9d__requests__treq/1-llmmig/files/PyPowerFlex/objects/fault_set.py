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
from twisted.internet.defer import inlineCallbacks

from PyPowerFlex import base_client
from PyPowerFlex import exceptions


LOG = logging.getLogger(__name__)


class FaultSet(base_client.EntityRequest):
    @inlineCallbacks
    def clear(self, fault_set_id):
        """Clear PowerFlex fault set.

        :type fault_set_id: str
        :rtype: dict
        """

        action = 'clearFaultSet'

        r, response = yield self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=fault_set_id)
        if r.code != 200:  # treq uses response.code instead of r.status_code
            response_text = yield response.text()
            msg = ('Failed to clear PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=fault_set_id,
                           response=response_text))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        result = yield self.get(entity_id=fault_set_id)
        return result

    @inlineCallbacks
    def create(self, protection_domain_id, name=None):
        """Create PowerFlex fault set.

        :type protection_domain_id: str
        :type name: str
        :rtype: dict
        """

        params = dict(
            protectionDomainId=protection_domain_id,
            name=name
        )

        result = yield self._create_entity(params)
        return result

    @inlineCallbacks
    def get_sdss(self, fault_set_id, filter_fields=None, fields=None):
        """Get related PowerFlex SDSs for fault set.

        :type fault_set_id: str
        :type filter_fields: dict
        :type fields: list|tuple
        :rtype: list[dict]
        """

        result = yield self.get_related(fault_set_id,
                                        'Sds',
                                        filter_fields,
                                        fields)
        return result

    @inlineCallbacks
    def delete(self, fault_set_id):
        """Remove PowerFlex fault set.

        :type fault_set_id: str
        :rtype: None
        """

        result = yield self._delete_entity(fault_set_id)
        return result

    @inlineCallbacks
    def rename(self, fault_set_id, name):
        """Rename PowerFlex fault set.

        :type fault_set_id: str
        :type name: str
        :rtype: dict
        """

        action = 'setFaultSetName'

        params = dict(
            newName=name
        )

        result = yield self._rename_entity(action, fault_set_id, params)
        return result

    @inlineCallbacks
    def query_selected_statistics(self, properties, ids=None):
        """Query PowerFlex fault set statistics.

        :type properties: list
        :type ids: list of fault set IDs or None for all fault sets
        :rtype: dict
        """

        action = "querySelectedStatistics"

        params = dict(properties=properties)

        if ids:
            params["ids"] = ids
        else:
            params["allIds"] = ""

        result = yield self._query_selected_statistics(action, params)
        return result
