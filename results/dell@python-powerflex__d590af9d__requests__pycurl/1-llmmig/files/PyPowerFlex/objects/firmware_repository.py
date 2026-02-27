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
from PyPowerFlex import utils
LOG = logging.getLogger(__name__)


class FirmwareRepository(base_client.EntityRequest):
    def send_get_request(self, url):
        """
        Perform an HTTP GET request using pycurl.
        :param url: The URL to send the GET request to.
        :return: A tuple containing the HTTP status code and the response body.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            msg = f"pycurl error occurred: {e}"
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        finally:
            curl.close()
        
        response_body = buffer.getvalue().decode('utf-8')
        return status_code, response_body

    def get(self, filters=None, limit=None, offset=None, sort=None, related=False, bundles=False, components=False):
        """
        Retrieve all firmware repository with filter, sort, pagination
        :param filters: (Optional) The filters to apply to the results.
        :param limit: (Optional) Page limit.
        :param offset: (Optional) Pagination offset.
        :param sort: (Optional) The field to sort the results by.
        :param related: Whether to include related entities in the response.
        :param bundles: Whether to include bundles in the response.
        :param components: Whether to include components in the response.
        :return: A list of dictionary containing the retrieved firmware repository.
        """
        params = dict(
            filter=filters,
            sort=sort,
            offset=offset,
            limit=limit,
            related=related,
            bundles=bundles,
            components=components
        )
        url = utils.build_uri_with_params(self.firmware_repository_url, **params)
        status_code, response = self.send_get_request(url)
        if status_code != 200:  # HTTP OK
            msg = (f'Failed to retrieve firmware repository. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return response
