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
import json
from io import BytesIO
from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
LOG = logging.getLogger(__name__)

class ServiceTemplate(base_client.EntityRequest):
    def send_get_request(self, url):
        """
        Helper method to send a GET request using pycurl.
        :param url: The URL to send the GET request to.
        :return: A tuple containing the HTTP status code and the response body (parsed as JSON).
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            curl.setopt(pycurl.CONNECTTIMEOUT, 10)
            curl.setopt(pycurl.TIMEOUT, 30)
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            msg = f'Failed to send GET request to {url}. Error: {e}'
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        finally:
            curl.close()

        response_body = buffer.getvalue().decode('utf-8')
        try:
            response_json = json.loads(response_body)
        except json.JSONDecodeError as e:
            msg = f'Failed to parse JSON response from {url}. Error: {e}'
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return status_code, response_json

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
        url = utils.build_uri_with_params(self.service_template_url, **params)
        status_code, response = self.send_get_request(url)
        if status_code != 200:
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
        status_code, response = self.send_get_request(url)
        if status_code != 200:
            msg = (f'Failed to retrieve service template by id {service_template_id}. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return response
