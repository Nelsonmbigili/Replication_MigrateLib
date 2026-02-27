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
import aiohttp
from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
LOG = logging.getLogger(__name__)


class Deployment(base_client.EntityRequest):
    async def get(self, filters=None, full=None, include_devices=None, include_template=None,
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
        async with aiohttp.ClientSession() as session:
            async with session.get(utils.build_uri_with_params(self.deployment_url, **params)) as r:
                response = await r.json()
                if r.status != 200:
                    msg = (f'Failed to retrieve deployments. Error: {response}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)
                return response

    async def get_by_id(self, deployment_id):
        """
        Retrieve Deployment for specified ID.
        :param deployment_id: Deployment ID.
        :return: A dictionary containing the retrieved Deployment.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.deployment_url}/{deployment_id}') as r:
                response = await r.json()
                if r.status != 200:
                    msg = (f'Failed to retrieve deployment by id {deployment_id}. Error: {response}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)
                return response

    async def validate(self, rg_data):
        """
        Validates a new deployment.
        Args:
            rg_data (dict): The resource group data to be deployed.
        Returns:
            dict: The response from the deployment API.
        Raises:
            PowerFlexClientException: If the deployment fails.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.deployment_url}/validate', json=rg_data) as r:
                response = await r.json()
                if r.status != 200:
                    msg = (f'Failed to validate the deployment. Error: {response}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)
                return response

    async def create(self, rg_data):
        """
        Creates a new deployment.
        Args:
            rg_data (dict): The resource group data to be deployed.
        Returns:
            dict: The response from the deployment API.
        Raises:
            PowerFlexClientException: If the deployment fails.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(self.deployment_url, json=rg_data) as r:
                response = await r.json()
                if r.status != 200:
                    msg = (f'Failed to create a new deployment. Error: {response}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)
                return response

    async def edit(self, deployment_id, rg_data):
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
        request_url = f'{self.deployment_url}/{deployment_id}'
        async with aiohttp.ClientSession() as session:
            async with session.put(request_url, json=rg_data) as r:
                response = await r.json()
                if r.status != 200:
                    msg = (f'Failed to edit the deployment. Error: {response}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)
                return response

    async def delete(self, deployment_id):
        """
        Deletes a deployment with the given ID.
        Args:
            deployment_id (str): The ID of the deployment to delete.
        Returns:
            str: The response from the delete request.
        Raises:
            exceptions.PowerFlexClientException: If the delete request fails.
        """
        request_url = f'{self.deployment_url}/{deployment_id}'
        async with aiohttp.ClientSession() as session:
            async with session.delete(request_url) as r:
                if r.status != 204:
                    response = await r.text()
                    msg = (f'Failed to delete deployment. Error: {response}')
                    LOG.error(msg)
                    raise exceptions.PowerFlexClientException(msg)
                return await r.text()
