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
import urllib3
from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
LOG = logging.getLogger(__name__)

class ManagedDevice(base_client.EntityRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http = urllib3.PoolManager()  # Initialize a PoolManager for HTTP requests

    def get(self, filters=None, limit=None, offset=None, sort=None):
        """
        Retrieve all devices from inventory with filter, sort, pagination
        :param filters: (Optional) The filters to apply to the results.
        :param limit: (Optional) Page limit.
        :param offset: (Optional) Pagination offset.
        :param sort: (Optional) The field to sort the results by.
        :return: A list of dictionary containing the retrieved devices from inventory.
        """
        params = dict(
            filter=filters,
            limit=limit,
            offset=offset,
            sort=sort
        )
        url = utils.build_uri_with_params(self.managed_device_url, **params)
        r, response = self.send_get_request(url)
        if r.status != 200:  # Replace requests.codes.ok with HTTP status code 200
            msg = (f'Failed to retrieve managed devices. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return response

    def send_get_request(self, url):
        """
        Send a GET request using urllib3.
        :param url: The URL to send the GET request to.
        :return: A tuple containing the HTTPResponse object and the parsed JSON response.
        """
        try:
            r = self.http.request('GET', url)
            response = utils.parse_json_response(r.data)  # Assuming utils.parse_json_response handles JSON parsing
            return r, response
        except urllib3.exceptions.HTTPError as e:
            LOG.error(f"HTTP request failed: {e}")
            raise exceptions.PowerFlexClientException(f"HTTP request failed: {e}")
