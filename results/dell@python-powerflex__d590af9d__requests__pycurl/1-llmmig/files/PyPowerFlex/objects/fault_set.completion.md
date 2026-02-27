### Explanation of Changes
The original code uses the `requests` library to send HTTP requests. To migrate to `pycurl`, the following changes were made:
1. **Replaced `requests` imports**: Removed the `requests` import and replaced it with `pycurl`.
2. **Rewrote the `send_post_request` method**: Since `pycurl` does not have a high-level API like `requests`, I implemented the equivalent functionality using `pycurl` for sending POST requests.
3. **Handled HTTP response codes**: `pycurl` does not directly provide response objects like `requests`. Instead, I captured the HTTP response code and body separately using `pycurl` options.
4. **Replaced `r.status_code` checks**: Replaced the `requests.codes.ok` check with a comparison of the HTTP response code captured from `pycurl`.

### Modified Code
Below is the entire code after migrating from `requests` to `pycurl`:

```python
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


LOG = logging.getLogger(__name__)


class FaultSet(base_client.EntityRequest):
    def send_post_request(self, url, action, entity, entity_id):
        """Send a POST request using pycurl.

        :param url: str, the URL to send the request to
        :param action: str, the action to perform
        :param entity: str, the entity type
        :param entity_id: str, the entity ID
        :return: tuple (HTTP response code, response body as dict)
        """
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.POST, 1)

        # Prepare the POST data
        post_data = json.dumps({
            "action": action,
            "entity": entity,
            "entityId": entity_id
        })
        c.setopt(c.POSTFIELDS, post_data)

        # Set headers
        c.setopt(c.HTTPHEADER, [
            'Content-Type: application/json',
            'Accept: application/json'
        ])

        # Capture the response
        c.setopt(c.WRITEDATA, buffer)

        # Perform the request
        try:
            c.perform()
            response_code = c.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            msg = f"Failed to send POST request: {e}"
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        finally:
            c.close()

        # Parse the response body
        response_body = buffer.getvalue().decode('utf-8')
        try:
            response_json = json.loads(response_body)
        except json.JSONDecodeError:
            response_json = response_body  # Return raw response if not JSON

        return response_code, response_json

    def clear(self, fault_set_id):
        """Clear PowerFlex fault set.

        :type fault_set_id: str
        :rtype: dict
        """

        action = 'clearFaultSet'

        r_code, response = self.send_post_request(self.base_action_url,
                                                  action=action,
                                                  entity=self.entity,
                                                  entity_id=fault_set_id)
        if r_code != 200:  # HTTP 200 OK
            msg = ('Failed to clear PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=fault_set_id,
                           response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=fault_set_id)

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
```

### Key Notes
- The `send_post_request` method was rewritten to use `pycurl` for sending POST requests.
- The `pycurl` library requires manual handling of HTTP response codes and response bodies, which was implemented using `pycurl.RESPONSE_CODE` and a `BytesIO` buffer.
- The rest of the code remains unchanged, as the migration only affects the HTTP request logic.