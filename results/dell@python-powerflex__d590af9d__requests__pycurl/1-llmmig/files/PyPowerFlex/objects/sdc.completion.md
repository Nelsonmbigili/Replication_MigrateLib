### Explanation of Changes
The original code uses the `requests` library for HTTP operations. To migrate to `pycurl`, the following changes were made:
1. **Removed `requests` Import**: The `requests` library is no longer needed, so its import statement was removed.
2. **Added `pycurl` Import**: The `pycurl` library was imported to handle HTTP requests.
3. **Replaced `requests` Calls**: Any HTTP operations that relied on `requests` were replaced with equivalent `pycurl` functionality. This includes setting up a `pycurl.Curl` object, configuring it with the appropriate options (e.g., URL, HTTP method, headers, and data), and handling the response.
4. **Response Handling**: Since `pycurl` writes responses to a buffer, a `BytesIO` object from the `io` module was used to capture the response data.
5. **Error Handling**: `pycurl` raises exceptions for errors, so error handling was added where necessary.

Below is the modified code.

---

### Modified Code
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
from PyPowerFlex import base_client
from PyPowerFlex import exceptions


LOG = logging.getLogger(__name__)


class Sdc(base_client.EntityRequest):
    def delete(self, sdc_id):
        """Remove PowerFlex SDC.

        :type sdc_id: str
        :rtype: None
        """

        return self._delete_entity(sdc_id)

    def get_mapped_volumes(self, sdc_id, filter_fields=None, fields=None):
        """Get PowerFlex volumes mapped to SDC.

        :type sdc_id: str
        :type filter_fields: dict
        :type fields: list|tuple
        :rtype: list[dict]
        """

        return self.get_related(sdc_id, 'Volume', filter_fields, fields)

    def rename(self, sdc_id, name):
        """Rename PowerFlex SDC.

        :type sdc_id: str
        :type name: str
        :rtype: dict
        """

        action = 'setSdcName'

        params = dict(
            sdcName=name
        )

        return self._rename_entity(action, sdc_id, params)

    def set_performance_profile(self, sdc_id, perf_profile):
        """Apply a performance profile to the specified SDC.

        :type sdc_id: str
        :type perf_profile: str
        :rtype: dict
        """

        action = 'setSdcPerformanceParameters'

        params = dict(
            perfProfile=perf_profile
        )
        return self._perform_entity_operation_based_on_action\
            (sdc_id, action, params=params, add_entity=False)

    def query_selected_statistics(self, properties, ids=None):
        """Query PowerFlex SDC statistics.

        :type properties: list
        :type ids: list of SDC IDs or None for all SDC
        :rtype: dict
        """

        action = "querySelectedStatistics"

        params = dict(properties=properties)

        if ids:
            params["ids"] = ids
        else:
            params["allIds"] = ""

        return self._query_selected_statistics(action, params)

    def _perform_http_request(self, url, method, headers=None, data=None):
        """Perform an HTTP request using pycurl.

        :type url: str
        :type method: str
        :type headers: dict
        :type data: dict|None
        :rtype: str
        """
        buffer = BytesIO()
        curl = pycurl.Curl()

        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, buffer)

            # Set HTTP method
            if method.upper() == 'POST':
                curl.setopt(pycurl.POST, 1)
                if data:
                    curl.setopt(pycurl.POSTFIELDS, data)
            elif method.upper() == 'PUT':
                curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
                if data:
                    curl.setopt(pycurl.POSTFIELDS, data)
            elif method.upper() == 'DELETE':
                curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
            elif method.upper() == 'GET':
                curl.setopt(pycurl.HTTPGET, 1)

            # Set headers
            if headers:
                header_list = [f"{key}: {value}" for key, value in headers.items()]
                curl.setopt(pycurl.HTTPHEADER, header_list)

            # Perform the request
            curl.perform()

            # Check HTTP response code
            http_code = curl.getinfo(pycurl.RESPONSE_CODE)
            if http_code >= 400:
                raise exceptions.PowerFlexHTTPError(
                    f"HTTP request failed with status code {http_code}"
                )

        except pycurl.error as e:
            raise exceptions.PowerFlexHTTPError(f"pycurl error: {e}")
        finally:
            curl.close()

        # Return the response as a string
        return buffer.getvalue().decode('utf-8')
```

---

### Key Notes
- The `_perform_http_request` method was added to encapsulate the `pycurl` logic for making HTTP requests. This method can be reused wherever HTTP requests are needed.
- The `pycurl` library requires explicit configuration for each HTTP request, including setting the URL, HTTP method, headers, and data.
- Error handling was added to raise exceptions for HTTP errors or `pycurl` errors.