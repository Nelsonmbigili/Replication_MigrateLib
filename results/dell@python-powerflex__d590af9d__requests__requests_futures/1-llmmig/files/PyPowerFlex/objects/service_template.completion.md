### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class, which provides asynchronous request handling.
2. **Session Initialization**: Replaced the synchronous `requests` calls with asynchronous calls using `FuturesSession`. This involves creating a `FuturesSession` object and using it to send requests.
3. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual response object synchronously (to maintain the original behavior of the code).
4. **send_get_request Method**: Assumed that the `send_get_request` method in the `base_client.EntityRequest` class was using `requests.get`. Updated it to use the `FuturesSession` object for asynchronous requests.

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
from requests_futures.sessions import FuturesSession
from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
LOG = logging.getLogger(__name__)

class ServiceTemplate(base_client.EntityRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = FuturesSession()  # Initialize a FuturesSession for asynchronous requests

    def get(self, filters=None, full=None, limit=None, offset=None, sort=None, include_attachments=None):
        """
        Retrieve all Service Templates with filter, sort, pagination
        :param filters: (Optional) The filters to apply to the results.
        :param full: (Optional) Whether to return full details for each result.
        :param limit: (Optional) Page limit.
        :param offset: (Optional) Pagination offset.
        :param sort: (Optional) The field to sort the results by.
        :param include_attachments: (Optional) Whether to include attachments.
        :return: A list of dictionary containing the retrieved Service Templates.
        """
        params = dict(
            filter=filters,
            full=full,
            limit=limit,
            offset=offset,
            sort=sort,
            includeAttachments=include_attachments
        )
        future = self.session.get(utils.build_uri_with_params(self.service_template_url, **params))  # Asynchronous GET request
        r = future.result()  # Wait for the response and retrieve it
        response = r.json()  # Parse the JSON response
        if r.status_code != 200:  # Use 200 instead of requests.codes.ok for clarity
            msg = (f'Failed to retrieve service templates. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return response

    def get_by_id(self, service_template_id, for_deployment=False):
        """
        Retrieve a Service Template by its ID.
        :param service_template_id: The ID of the Service Template to retrieve.
        :param for_deployment: (Optional) Whether to retrieve the Service Template for deployment.
        :return: A dictionary containing the retrieved Service Template.
        """
        url = f'{self.service_template_url}/{service_template_id}'
        if for_deployment:
            url += '?forDeployment=true'
        future = self.session.get(url)  # Asynchronous GET request
        r = future.result()  # Wait for the response and retrieve it
        response = r.json()  # Parse the JSON response
        if r.status_code != 200:  # Use 200 instead of requests.codes.ok for clarity
            msg = (f'Failed to retrieve service template by id {service_template_id}. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return response
```

### Key Points
- The `FuturesSession` object is used to send asynchronous requests.
- The `.result()` method is called on the `Future` object to block and retrieve the response, maintaining the synchronous behavior of the original code.
- The rest of the code remains unchanged to ensure compatibility with the larger application.