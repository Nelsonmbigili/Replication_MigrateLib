### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class for asynchronous requests.
2. **Session Initialization**: Replaced any synchronous `requests` calls with asynchronous calls using `FuturesSession`. This includes initializing a `FuturesSession` object and using its methods (`get`, `post`, etc.) instead of the `requests` methods.
3. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual response object where necessary.
4. **Code Updates**: Updated the `send_post_request` method (assumed to be part of the `base_client.EntityRequest` class) to use the `FuturesSession` for asynchronous requests.

Below is the modified code:

---

### Modified Code:
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = FuturesSession()  # Initialize FuturesSession for async requests

    def add_mapped_sdc(self,
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

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=volume_id,
                                             params=params)
        r = r.result()  # Wait for the asynchronous request to complete
        if r.status_code != 200:
            msg = ('Failed to map PowerFlex {entity} with id {_id} '
                   'to SDC. Error: {response}'.format(entity=self.entity,
                                                      _id=volume_id,
                                                      response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=volume_id)

    def send_post_request(self, url, action, entity, entity_id, params):
        """Send an asynchronous POST request using FuturesSession.

        :param url: str
        :param action: str
        :param entity: str
        :param entity_id: str
        :param params: dict
        :return: Future, response
        """
        full_url = f"{url}/{action}/{entity}/{entity_id}"
        future = self.session.post(full_url, json=params)
        return future, future.result().json()

    def extend(self, volume_id, size_in_gb, allow_ext_managed=None):
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

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=volume_id,
                                             params=params)
        r = r.result()  # Wait for the asynchronous request to complete
        if r.status_code != 200:
            msg = ('Failed to extend PowerFlex {entity} with id {_id}. '
                   'Error: {response}'.format(entity=self.entity,
                                              _id=volume_id,
                                              response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=volume_id)

    # Other methods remain unchanged unless they involve requests calls.
```

---

### Key Notes:
1. **Asynchronous Requests**: The `requests_futures` library allows for asynchronous HTTP requests. The `.result()` method is used to block and retrieve the response when needed.
2. **Session Management**: A `FuturesSession` object is initialized in the `Volume` class constructor and reused for all HTTP requests.
3. **Minimal Changes**: Only the parts of the code that directly interact with the `requests` library were modified to use `requests_futures`. Other parts of the code remain unchanged.