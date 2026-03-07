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
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import pycurl
from io import BytesIO
from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils
LOG = logging.getLogger(__name__)

class Deployment(base_client.EntityRequest):
    def send_get_request(self, url):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.NOBODY, False)
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        return response_code, buffer.getvalue().decode('utf-8')

    def send_post_request(self, url, data):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.POSTFIELDS, utils.json.dumps(data))
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        return response_code, buffer.getvalue().decode('utf-8')

    def send_put_request(self, url, data):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.CUSTOMREQUEST, "PUT")
        c.setopt(c.POSTFIELDS, utils.json.dumps(data))
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        return response_code, buffer.getvalue().decode('utf-8')

    def send_delete_request(self, url):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.CUSTOMREQUEST, "DELETE")
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()
        return response_code, buffer.getvalue().decode('utf-8')

    def get(self, filters=None, full=None, include_devices=None, include_template=None,
            limit=None, offset=None, sort=None):
        params = dict(
            filter=filters,
            full=full,
            sort=sort,
            offset=offset,
            limit=limit,
            includeDevices=include_devices,
            includeTemplate=include_template
        )
        r, response = self.send_get_request(utils.build_uri_with_params(self.deployment_url, **params))
        if r != 200:
            msg = (f'Failed to retrieve deployments. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return response

    def get_by_id(self, deployment_id):
        r, response = self.send_get_request(f'{self.deployment_url}/{deployment_id}')
        if r != 200:
            msg = (f'Failed to retrieve deployment by id {deployment_id}. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        return response

    def validate(self, rg_data):
        r, response = self.send_post_request(f'{self.deployment_url}/validate', rg_data)
        if r != 200:
            msg = (f'Failed to validate the deployment. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    def create(self, rg_data):
        r, response = self.send_post_request(self.deployment_url, rg_data)
        if r != 200:
            msg = (f'Failed to create a new deployment. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    def edit(self, deployment_id, rg_data):
        request_url = f'{self.deployment_url}/{deployment_id}'
        r, response = self.send_put_request(request_url, rg_data)
        
        if r != 200:
            msg = (f'Failed to edit the deployment. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response

    def delete(self, deployment_id):
        request_url = f'{self.deployment_url}/{deployment_id}'
        r, response = self.send_delete_request(request_url)

        if r != 204:
            msg = (f'Failed to delete deployment. Error: {response}')
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return response
