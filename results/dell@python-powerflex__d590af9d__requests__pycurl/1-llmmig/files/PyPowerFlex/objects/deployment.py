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


class Deployment(base_client.EntityRequest):
    def _send_request(self, method, url, data=None):
        """
        Helper function to send HTTP requests using pycurl.
        :param method: HTTP method (GET, POST, PUT, DELETE).
        :param url: The URL for the request.
        :param data: (Optional) Data to send in the request body (for POST/PUT).
        :return: A tuple containing the HTTP status code and the response body.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.setopt(pycurl.CUSTOMREQUEST, method)

        if data:
            curl.setopt(pycurl.POSTFIELDS, json.dumps(data))
            curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            LOG.error(f"pycurl error: {e}")
            raise exceptions.PowerFlexClientException(f"pycurl error: {e}")
        finally:
            curl.close()

        response_body = buffer.getvalue().decode('utf-8')
        return status_code, response_body

    def get(self, filters=None, full=None, include_devices=None, include_template=None,
            limit=None, offset=None, sort=None):
        """
        Retrieve all Deployments with filter, sort, pagination
        :param filters: (Optional) The filters to apply to the results.
        :param full: (Optional) Whether to return full details for each result.
        :param include_devices: (Optional) Whether to include devices in the response.
        :param include_template: (Optional) Whether to include service templates in the response.
        :param limit: (Optional) Page limit.
        :param offset: (Optional) Pagination offset.
        :param sort: (Optional) The field to sort the results by.
        :return: A list of dictionary containing the retrieved Deployments.
        """
        params = dict(
            filter=filters,
            full=full,
            sort=sort,
            offset=offset,
            limit=limit,
            includeDevices=include_devices,
            includeTemplate=include_template
        )
        url = utils.build_uri_with_params(self.deployment_url, **params)
        status_code, response = self._send_request('GET', url)

        if status_code != 200:
            msg = (f'Failed to retrieve deployments. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return json.loads(response)

    def get_by_id(self, deployment_id):
        """
        Retrieve Deployment for specified ID.
        :param deployment_id: Deployment ID.
        :return: A dictionary containing the retrieved Deployment.
        """
        url = f'{self.deployment_url}/{deployment_id}'
        status_code, response = self._send_request('GET', url)

        if status_code != 200:
            msg = (f'Failed to retrieve deployment by id {deployment_id}. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return json.loads(response)

    def validate(self, rg_data):
        """
        Validates a new deployment.
        Args:
            rg_data (dict): The resource group data to be deployed.
        Returns:
            dict: The response from the deployment API.
        Raises:
            PowerFlexClientException: If the deployment fails.
        """
        url = f'{self.deployment_url}/validate'
        status_code, response = self._send_request('POST', url, rg_data)

        if status_code != 200:
            msg = (f'Failed to validate the deployment. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return json.loads(response)

    def create(self, rg_data):
        """
        Creates a new deployment.
        Args:
            rg_data (dict): The resource group data to be deployed.
        Returns:
            dict: The response from the deployment API.
        Raises:
            PowerFlexClientException: If the deployment fails.
        """
        url = self.deployment_url
        status_code, response = self._send_request('POST', url, rg_data)

        if status_code != 200:
            msg = (f'Failed to create a new deployment. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return json.loads(response)

    def edit(self, deployment_id, rg_data):
        """
        Edit a deployment with the given ID using the provided data.
        Args:
            deployment_id (str): The ID of the deployment to edit.
            rg_data (dict): The data to use for editing the deployment.
        Returns:
            dict: The response from the API.
        Raises:
            PowerFlexClientException: If the request fails.
        """
        url = f'{self.deployment_url}/{deployment_id}'
        status_code, response = self._send_request('PUT', url, rg_data)

        if status_code != 200:
            msg = (f'Failed to edit the deployment. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return json.loads(response)

    def delete(self, deployment_id):
        """
        Deletes a deployment with the given ID.
        Args:
            deployment_id (str): The ID of the deployment to delete.
        Returns:
            str: The response from the delete request.
        Raises:
            exceptions.PowerFlexClientException: If the delete request fails.
        """
        url = f'{self.deployment_url}/{deployment_id}'
        status_code, response = self._send_request('DELETE', url)

        if status_code != 204:
            msg = (f'Failed to delete deployment. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response
