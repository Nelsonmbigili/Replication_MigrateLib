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
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import pycurl
from io import BytesIO

from PyPowerFlex import base_client
from PyPowerFlex import exceptions


LOG = logging.getLogger(__name__)


class FaultSet(base_client.EntityRequest):
    def clear(self, fault_set_id):
        """Clear PowerFlex fault set.

        :type fault_set_id: str
        :rtype: dict
        """

        action = 'clearFaultSet'

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=fault_set_id)
        if r.getinfo(pycurl.RESPONSE_CODE) != 200:
            msg = ('Failed to clear PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=fault_set_id,
                           response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=fault_set_id)

    def send_post_request(self, url, action, entity, entity_id):
        """Send a POST request using pycurl."""
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, f"{url}/{action}/{entity}/{entity_id}")
        c.setopt(c.POST, 1)
        c.setopt(c.WRITEFUNCTION, buffer.write)

        # You may need to set additional options here based on your API requirements
        # For example, if you need to send JSON data, you would set:
        # c.setopt(c.POSTFIELDS, json.dumps(data))
        # c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])

        c.perform()
        response = buffer.getvalue().decode('utf-8')
        c.close()

        return c, response

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

        return self._create_entity(params)

    def get_sdss(self, fault_set_id, filter_fields=None, fields=None):
        """Get related PowerFlex SDSs for fault set.

        :type fault_set_id: str
        :type filter_fields: dict
        :type fields: list|tuple
        :rtype: list[dict]
        """

        return self.get_related(fault_set_id,
                                'Sds',
                                filter_fields,
                                fields)

    def delete(self, fault_set_id):
        """Remove PowerFlex fault set.

        :type fault_set_id: str
        :rtype: None
        """

        return self._delete_entity(fault_set_id)

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

        return self._rename_entity(action, fault_set_id, params)

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

        return self._query_selected_statistics(action, params)
