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
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from PyPowerFlex import exceptions
from PyPowerFlex import utils

urllib3.disable_warnings(InsecureRequestWarning)
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
        self.http = urllib3.PoolManager(cert_reqs='CERT_NONE')  # Default to no cert verification

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

    def send_request(self, method, url, params=None, **url_params):
        params = params or {}
        request_url = f"{self.base_url}{url.format(**url_params)}"
        version = self.login()
        headers = self.get_auth_headers(method)
        timeout = self.configuration.timeout

        if utils.is_version_3(version):
            auth = (self.configuration.username, self.token.get())
            del headers['Authorization']
        else:
            auth = None

        body = None
        if method in [self.PUT, self.POST]:
            body = utils.prepare_params(params)

        try:
            response = self.http.request(
                method.upper(),
                request_url,
                headers=headers,
                body=body,
                timeout=timeout,
                cert_reqs='CERT_REQUIRED' if self.verify_certificate else 'CERT_NONE',
                ca_certs=self.verify_certificate if isinstance(self.verify_certificate, str) else None
            )
        except urllib3.exceptions.HTTPError as e:
            LOG.error(f"HTTP request failed: {e}")
            raise

        self.logout(version)
        return response

    def send_get_request(self, url, params=None, **url_params):
        response = self.send_request(self.GET, url, params, **url_params)
        return response, json.loads(response.data.decode('utf-8'))

    def send_post_request(self, url, params=None, **url_params):
        response = self.send_request(self.POST, url, params, **url_params)
        return response, json.loads(response.data.decode('utf-8'))

    def send_put_request(self, url, params=None, **url_params):
        response = self.send_request(self.PUT, url, params, **url_params)
        return response, json.loads(response.data.decode('utf-8'))

    def send_delete_request(self, url, params=None, **url_params):
        return self.send_request(self.DELETE, url, params, **url_params)

    def send_mdm_cluster_post_request(self, url, params=None, **url_params):
        if params is None:
            params = dict()
        response = None
        version = self.login()
        request_url = self.base_url + url.format(**url_params)
        body = utils.prepare_params(params)

        try:
            r = self.http.request(
                'POST',
                request_url,
                headers=self.headers,
                body=body,
                timeout=self.configuration.timeout,
                cert_reqs='CERT_REQUIRED' if self.verify_certificate else 'CERT_NONE',
                ca_certs=self.verify_certificate if isinstance(self.verify_certificate, str) else None
            )
        except urllib3.exceptions.HTTPError as e:
            LOG.error(f"HTTP request failed: {e}")
            raise

        if r.data:
            response = json.loads(r.data.decode('utf-8'))
        self.logout(version)
        return r, response

    # To perform login based on the API version
    def login(self):
        version = self.get_api_version()
        if utils.is_version_3(version=version):
            self._login()
        else:
            self._appliance_login()
        return version

    # To perform logout based on the API version
    def logout(self, version):
        if utils.is_version_3(version=version):
            self._logout()
        else:
            self._appliance_logout()

    # Get the Current API version
    def get_api_version(self):
        request_url = self.base_url + '/version'
        self._login()
        try:
            r = self.http.request(
                'GET',
                request_url,
                headers=self.headers,
                timeout=self.configuration.timeout,
                cert_reqs='CERT_REQUIRED' if self.verify_certificate else 'CERT_NONE',
                ca_certs=self.verify_certificate if isinstance(self.verify_certificate, str) else None
            )
        except urllib3.exceptions.HTTPError as e:
            LOG.error(f"HTTP request failed: {e}")
            raise

        return json.loads(r.data.decode('utf-8'))

    # API Login method for 4.0 and above.
    def _appliance_login(self):
        request_url = self.auth_url + '/login'
        payload = json.dumps({
            "username": self.configuration.username,
            "password": self.configuration.password
        })

        try:
            r = self.http.request(
                'POST',
                request_url,
                headers=self.headers,
                body=payload,
                timeout=self.configuration.timeout,
                cert_reqs='CERT_REQUIRED' if self.verify_certificate else 'CERT_NONE',
                ca_certs=self.verify_certificate if isinstance(self.verify_certificate, str) else None
            )
        except urllib3.exceptions.HTTPError as e:
            LOG.error(f"HTTP request failed: {e}")
            raise

        if r.status != 200:
            exc = exceptions.PowerFlexFailQuerying('token')
            LOG.error(exc.message)
            raise exc

        response = json.loads(r.data.decode('utf-8'))
        token = response['access_token']
        self.token.set(token)
        self.__refresh_token = response['refresh_token']

    # API logout method for 4.0 and above.
    def _appliance_logout(self):
        request_url = self.auth_url + '/logout'
        data = json.dumps({'refresh_token': '{0}'.format(self.__refresh_token)})

        try:
            r = self.http.request(
                'POST',
                request_url,
                headers=self.get_auth_headers(),
                body=data,
                timeout=self.configuration.timeout,
                cert_reqs='CERT_REQUIRED' if self.verify_certificate else 'CERT_NONE',
                ca_certs=self.verify_certificate if isinstance(self.verify_certificate, str) else None
            )
        except urllib3.exceptions.HTTPError as e:
            LOG.error(f"HTTP request failed: {e}")
            raise

        if r.status != 204:
            exc = exceptions.PowerFlexFailQuerying('token')
            LOG.error(exc.message)
            raise exc
        self.token.set("")
        self.__refresh_token = None

    def _login(self):
        request_url = self.base_url + '/login'
        try:
            r = self.http.request(
                'GET',
                request_url,
                headers=self.headers,
                timeout=self.configuration.timeout,
                cert_reqs='CERT_REQUIRED' if self.verify_certificate else 'CERT_NONE',
                ca_certs=self.verify_certificate if isinstance(self.verify_certificate, str) else None
            )
            if r.status != 200:
                raise urllib3.exceptions.HTTPError(f"Login failed with status {r.status}")
            token = json.loads(r.data.decode('utf-8'))
            self.token.set(token)
        except urllib3.exceptions.HTTPError as e:
            error_msg = f'Login failed with error: {str(e)}'
            LOG.error(error_msg)
            raise Exception(error_msg)

    def _logout(self):
        token = self.token.get()

        if token:
            request_url = self.base_url + '/logout'
            try:
                r = self.http.request(
                    'GET',
                    request_url,
                    headers=self.headers,
                    timeout=self.configuration.timeout,
                    cert_reqs='CERT_REQUIRED' if self.verify_certificate else 'CERT_NONE',
                    ca_certs=self.verify_certificate if isinstance(self.verify_certificate, str) else None
                )
                if r.status != 200:
                    raise urllib3.exceptions.HTTPError(f"Logout failed with status {r.status}")
            except urllib3.exceptions.HTTPError as e:
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

    def _create_entity(self, params=None):
        r, response = self.send_post_request(
            self.base_entity_list_or_create_url,
            entity=self.entity,
            params=params
        )
        if r.status_code != requests.codes.ok:
            exc = exceptions.PowerFlexFailCreating(self.entity, response)
            LOG.error(exc.message)
            raise exc

        entity_id = response['id']
        return self.get(entity_id=entity_id)

    def _delete_entity(self, entity_id, params=None):
        action = 'remove' + self.entity

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=entity_id,
                                             params=params)
        if r.status_code != requests.codes.ok:
            exc = exceptions.PowerFlexFailDeleting(self.entity, entity_id,
                                                   response)
            LOG.error(exc.message)
            raise exc

    def _rename_entity(self, action, entity_id, params=None):
        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=entity_id,
                                             params=params)
        if r.status_code != requests.codes.ok:
            exc = exceptions.PowerFlexFailRenaming(self.entity, entity_id,
                                                   response)
            LOG.error(exc.message)
            raise exc

        return self.get(entity_id=entity_id)

    def get(self, entity_id=None, filter_fields=None, fields=None):
        url = self.base_entity_list_or_create_url
        url_params = dict(entity=self.entity)

        if entity_id:
            url = self.base_entity_url
            url_params['entity_id'] = entity_id
            if filter_fields:
                msg = 'Can not apply filtering while querying entity by id.'
                raise exceptions.InvalidInput(msg)

        r, response = self.send_get_request(url, **url_params)
        if r.status_code != requests.codes.ok:
            exc = exceptions.PowerFlexFailQuerying(self.entity, entity_id,
                                                   response)
            LOG.error(exc.message)
            raise exc
        if filter_fields:
            response = utils.filter_response(response, filter_fields)
        if fields:
            response = utils.query_response_fields(response, fields)
        return response

    def get_related(self, entity_id, related, filter_fields=None,
                    fields=None):
        url_params = dict(
            entity=self.entity,
            entity_id=entity_id,
            related=related
        )

        r, response = self.send_get_request(self.base_relationship_url,
                                            **url_params)
        if r.status_code != requests.codes.ok:
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

    def _perform_entity_operation_based_on_action(self, entity_id, action,
                                                  params=None, add_entity=True, **url_params):
        if add_entity:
            action = action + self.entity

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=entity_id,
                                             params=params,
                                             **url_params)
        if r.status_code != requests.codes.ok:
            exc = exceptions.PowerFlexFailEntityOperation(self.entity, entity_id,
                                                          action, response)
            LOG.error(exc.message)
            raise exc

    def _query_selected_statistics(self, action, params=None):
        r, response = self.send_post_request(self.base_type_special_action_url,
                                             action=action,
                                             entity=self.entity,
                                             params=params)
        if r.status_code != requests.codes.ok:
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