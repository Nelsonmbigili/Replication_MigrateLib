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
import aiohttp
import asyncio
import ssl

from PyPowerFlex import exceptions
from PyPowerFlex import utils

LOG = logging.getLogger(__name__)


class Request:
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"

    def __init__(self, token, configuration):
        self.token = token
        self.configuration = configuration
        self.__refresh_token = None

    @property
    def base_url(self):
        return 'https://{address}:{port}/api'.format(
            address=self.configuration.gateway_address,
            port=self.configuration.gateway_port
        )

    @property
    def auth_url(self):
        return 'https://{address}:{port}/rest/auth'.format(
            address=self.configuration.gateway_address,
            port=self.configuration.gateway_port
        )

    @property
    def headers(self):
        return {'content-type': 'application/json'}

    @property
    def verify_certificate(self):
        verify_certificate = self.configuration.verify_certificate
        if (
                self.configuration.verify_certificate
                and self.configuration.certificate_path
        ):
            verify_certificate = self.configuration.certificate_path
        return verify_certificate

    def get_auth_headers(self, request_type=None):
        if request_type == self.GET:
            return {'Authorization': 'Bearer {0}'.format(self.token.get())}
        return {'Authorization': 'Bearer {0}'.format(self.token.get()),
                'content-type': 'application/json'}

    async def send_request(self, method, url, params=None, **url_params):
        params = params or {}
        request_url = f"{self.base_url}{url.format(**url_params)}"
        version = await self.login()
        ssl_context = None
        if not self.verify_certificate:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        timeout = aiohttp.ClientTimeout(total=self.configuration.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            request_params = {
                'headers': self.get_auth_headers(method),
                'ssl': ssl_context
            }
            if utils.is_version_3(version):
                request_params['auth'] = aiohttp.BasicAuth(
                    self.configuration.username, self.token.get())
                del request_params['headers']['Authorization']

            if method in [self.PUT, self.POST]:
                request_params['data'] = utils.prepare_params(params)

            async with session.request(method.upper(), request_url, **request_params) as response:
                response.raise_for_status()
                self.logout(version)
                return response

    async def send_get_request(self, url, params=None, **url_params):
        response = await self.send_request(self.GET, url, params, **url_params)
        return response, await response.json()

    async def send_post_request(self, url, params=None, **url_params):
        response = await self.send_request(self.POST, url, params, **url_params)
        return response, await response.json()

    async def send_put_request(self, url, params=None, **url_params):
        response = await self.send_request(self.PUT, url, params, **url_params)
        return response, await response.json()

    async def send_delete_request(self, url, params=None, **url_params):
        return await self.send_request(self.DELETE, url, params, **url_params)

    async def send_mdm_cluster_post_request(self, url, params=None, **url_params):
        if params is None:
            params = dict()
        response = None
        version = await self.login()
        request_url = self.base_url + url.format(**url_params)
        ssl_context = None
        if not self.verify_certificate:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        timeout = aiohttp.ClientTimeout(total=self.configuration.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                request_url,
                auth=aiohttp.BasicAuth(
                    self.configuration.username, self.token.get()
                ),
                headers=self.headers,
                data=utils.prepare_params(params),
                ssl=ssl_context
            ) as r:
                if await r.text() != '':
                    response = await r.json()
                await self.logout(version)
                return r, response

    async def login(self):
        version = await self.get_api_version()
        if utils.is_version_3(version=version):
            await self._login()
        else:
            await self._appliance_login()
        return version

    async def logout(self, version):
        if utils.is_version_3(version=version):
            await self._logout()
        else:
            await self._appliance_logout()

    async def get_api_version(self):
        request_url = self.base_url + '/version'
        await self._login()
        ssl_context = None
        if not self.verify_certificate:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        timeout = aiohttp.ClientTimeout(total=self.configuration.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                request_url,
                auth=aiohttp.BasicAuth(
                    self.configuration.username, self.token.get()
                ),
                ssl=ssl_context
            ) as r:
                response = await r.json()
                return response

    async def _appliance_login(self):
        request_url = self.auth_url + '/login'
        payload = {"username": "%s" % self.configuration.username,
                   "password": "%s" % self.configuration.password
                   }
        ssl_context = None
        if not self.verify_certificate:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        timeout = aiohttp.ClientTimeout(total=self.configuration.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                request_url,
                headers=self.headers,
                json=payload,
                ssl=ssl_context
            ) as r:
                if r.status != 200:
                    exc = exceptions.PowerFlexFailQuerying('token')
                    LOG.error(exc.message)
                    raise exc
                response = await r.json()
                token = response['access_token']
                self.token.set(token)
                self.__refresh_token = response['refresh_token']

    async def _appliance_logout(self):
        request_url = self.auth_url + '/logout'
        data = {'refresh_token': '{0}'.format(self.__refresh_token)}
        ssl_context = None
        if not self.verify_certificate:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        timeout = aiohttp.ClientTimeout(total=self.configuration.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                request_url,
                headers=self.get_auth_headers(),
                json=data,
                ssl=ssl_context
            ) as r:
                if r.status != 204:
                    exc = exceptions.PowerFlexFailQuerying('token')
                    LOG.error(exc.message)
                    raise exc
                self.token.set("")
                self.__refresh_token = None

    async def _login(self):
        request_url = self.base_url + '/login'
        ssl_context = None
        if not self.verify_certificate:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        timeout = aiohttp.ClientTimeout(total=self.configuration.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(
                    request_url,
                    auth=aiohttp.BasicAuth(
                        self.configuration.username, self.configuration.password
                    ),
                    ssl=ssl_context
                ) as r:
                    r.raise_for_status()
                    token = await r.json()
                    self.token.set(token)
            except aiohttp.ClientError as e:
                error_msg = f'Login failed with error:{e}'
                LOG.error(error_msg)
                raise Exception(error_msg)

    async def _logout(self):
        token = self.token.get()

        if token:
            request_url = self.base_url + '/logout'
            ssl_context = None
            if not self.verify_certificate:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            timeout = aiohttp.ClientTimeout(total=self.configuration.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    request_url,
                    auth=aiohttp.BasicAuth(
                        self.configuration.username, token
                    ),
                    ssl=ssl_context
                ) as r:
                    if r.status != 200:
                        exc = exceptions.PowerFlexFailQuerying('token')
                        LOG.error(exc.message)
                        raise exc
                    self.token.set("")


class EntityRequest(Request):
    base_action_url = '/instances/{entity}::{entity_id}/action/{action}'
    base_entity_url = '/instances/{entity}::{entity_id}'
    base_entity_list_or_create_url = '/types/{entity}/instances'
    base_relationship_url = base_entity_url + '/relationships/{related}'
    base_object_url = '/instances/{entity}/action/{action}'
    base_type_special_action_url = '/types/{entity}/instances/action/{action}'
    query_mdm_cluster_url = '/instances/{entity}/queryMdmCluster'
    list_statistics_url = '/types/{entity}/instances/action/{action}'
    service_template_url = '/V1/ServiceTemplate'
    managed_device_url = '/V1/ManagedDevice'
    deployment_url = '/V1/Deployment'
    firmware_repository_url = '/V1/FirmwareRepository'
    entity_name = None

    @property
    def entity(self):
        return self.entity_name or self.__class__.__name__

    async def _create_entity(self, params=None):
        r, response = await self.send_post_request(
            self.base_entity_list_or_create_url,
            entity=self.entity,
            params=params
        )
        if r.status != 200:
            exc = exceptions.PowerFlexFailCreating(self.entity, response)
            LOG.error(exc.message)
            raise exc

        entity_id = response['id']
        return await self.get(entity_id=entity_id)

    async def _delete_entity(self, entity_id, params=None):
        action = 'remove' + self.entity

        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=entity_id,
                                                   params=params)
        if r.status != 200:
            exc = exceptions.PowerFlexFailDeleting(self.entity, entity_id,
                                                   response)
            LOG.error(exc.message)
            raise exc

    async def _rename_entity(self, action, entity_id, params=None):
        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=entity_id,
                                                   params=params)
        if r.status != 200:
            exc = exceptions.PowerFlexFailRenaming(self.entity, entity_id,
                                                   response)
            LOG.error(exc.message)
            raise exc

        return await self.get(entity_id=entity_id)

    async def get(self, entity_id=None, filter_fields=None, fields=None):
        url = self.base_entity_list_or_create_url
        url_params = dict(entity=self.entity)

        if entity_id:
            url = self.base_entity_url
            url_params['entity_id'] = entity_id
            if filter_fields:
                msg = 'Can not apply filtering while querying entity by id.'
                raise exceptions.InvalidInput(msg)

        r, response = await self.send_get_request(url, **url_params)
        if r.status != 200:
            exc = exceptions.PowerFlexFailQuerying(self.entity, entity_id,
                                                   response)
            LOG.error(exc.message)
            raise exc
        if filter_fields:
            response = utils.filter_response(response, filter_fields)
        if fields:
            response = utils.query_response_fields(response, fields)
        return response

    async def get_related(self, entity_id, related, filter_fields=None,
                          fields=None):
        url_params = dict(
            entity=self.entity,
            entity_id=entity_id,
            related=related
        )

        r, response = await self.send_get_request(self.base_relationship_url,
                                                  **url_params)
        if r.status != 200:
            msg = (
                'Failed to query related {related} entities for PowerFlex '
                '{entity} with id {_id}.'
                ' Error: {response}'.format(related=related,
                                            entity=self.entity,
                                            _id=entity_id,
                                            response=response)
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)
        if filter_fields:
            response = utils.filter_response(response, filter_fields)
        if fields:
            response = utils.query_response_fields(response, fields)
        return response

    async def _perform_entity_operation_based_on_action(self, entity_id, action,
                                                        params=None, add_entity=True, **url_params):
        if add_entity:
            action = action + self.entity

        r, response = await self.send_post_request(self.base_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   entity_id=entity_id,
                                                   params=params,
                                                   **url_params)
        if r.status != 200:
            exc = exceptions.PowerFlexFailEntityOperation(self.entity, entity_id,
                                                          action, response)
            LOG.error(exc.message)
            raise exc

    async def _query_selected_statistics(self, action, params=None):
        r, response = await self.send_post_request(self.base_type_special_action_url,
                                                   action=action,
                                                   entity=self.entity,
                                                   params=params)
        if r.status != 200:
            exc = exceptions.PowerFlexFailQuerying(self.entity,
                                                   response=response,
                                                   entity_id=params["ids"]
                                                   if "ids" in params
                                                   else "all IDs"
                                                   if "allIds" in params
                                                   else None)
            LOG.error(exc.message)
            raise exc
        return response