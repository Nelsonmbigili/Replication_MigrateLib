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

class ManagedDevice(base_client.EntityRequest):
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
        
        # Prepare to capture the response
        response_buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            # Set up the curl request
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            curl.setopt(pycurl.TIMEOUT, 30)  # Set a timeout for the request
            
            # Perform the request
            curl.perform()
            
            # Get the HTTP response code
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            
            # Decode the response
            response = response_buffer.getvalue().decode('utf-8')
            
            # Check for HTTP success
            if status_code != 200:  # Equivalent to requests.codes.ok
                msg = (f'Failed to retrieve managed devices. HTTP Status: {status_code}, Error: {response}')
                LOG.error(msg)
                raise exceptions.PowerFlexClientException(msg)
            
            return response
        
        except pycurl.error as e:
            error_msg = f'Failed to retrieve managed devices. Pycurl error: {e}'
            LOG.error(error_msg)
            raise exceptions.PowerFlexClientException(error_msg)
        
        finally:
            # Clean up
            curl.close()
            response_buffer.close()
