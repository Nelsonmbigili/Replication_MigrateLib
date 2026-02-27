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
from PyPowerFlex.objects import Sds


LOG = logging.getLogger(__name__)


class StoragePool(base_client.EntityRequest):
    def send_post_request(self, url, action, entity, entity_id, params=None):
        """Send a POST request using pycurl.

        :param url: Base URL for the request
        :param action: Action to perform
        :param entity: Entity type
        :param entity_id: ID of the entity
        :param params: Parameters for the POST request
        :return: Tuple of HTTP response code and response body
        """
        full_url = f"{url}/{action}/{entity}/{entity_id}"
        response_buffer = BytesIO()
        curl = pycurl.Curl()

        try:
            # Set URL and method
            curl.setopt(pycurl.URL, full_url)
            curl.setopt(pycurl.POST, 1)

            # Set headers
            headers = [
                "Content-Type: application/json",
                f"Authorization: Bearer {self.token}"
            ]
            curl.setopt(pycurl.HTTPHEADER, headers)

            # Set POST data
            if params:
                import json
                post_data = json.dumps(params)
                curl.setopt(pycurl.POSTFIELDS, post_data)

            # Capture response
            curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)

            # Perform the request
            curl.perform()

            # Get HTTP response code
            http_code = curl.getinfo(pycurl.RESPONSE_CODE)

        except pycurl.error as e:
            error_msg = f"pycurl error: {e}"
            LOG.error(error_msg)
            raise exceptions.PowerFlexClientException(error_msg)

        finally:
            curl.close()

        # Decode response
        response_body = response_buffer.getvalue().decode('utf-8')
        return http_code, response_body

    def set_checksum_enabled(self, storage_pool_id, checksum_enabled):
        """Enable/disable checksum for PowerFlex storage pool.

        :type storage_pool_id: str
        :type checksum_enabled: bool
        :rtype: dict
        """

        action = 'setChecksumEnabled'

        params = dict(
            checksumEnabled=checksum_enabled
        )

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=storage_pool_id,
                                             params=params)
        if r != 200:  # HTTP 200 OK
            msg = (f'Failed to enable/disable checksum for PowerFlex {self.entity} '
                   f'with id {storage_pool_id}. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=storage_pool_id)

    def set_compression_method(self, storage_pool_id, compression_method):
        """Set compression method for PowerFlex storage pool.

        :type storage_pool_id: str
        :type compression_method: str
        :rtype: dict
        """

        action = 'modifyCompressionMethod'

        params = dict(
            compressionMethod=compression_method
        )

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=storage_pool_id,
                                             params=params)
        if r != 200:  # HTTP 200 OK
            msg = (f'Failed to set compression method for PowerFlex {self.entity} '
                   f'with id {storage_pool_id}. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=storage_pool_id)

    # Other methods remain unchanged, as they rely on send_post_request
