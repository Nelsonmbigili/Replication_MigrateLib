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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import pycurl
from io import BytesIO
from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils

LOG = logging.getLogger(__name__)


class SdtIp(dict):
    """PowerFlex sdt ip object.

    JSON-serializable, should be used as `sdt_ips` list item
    in `Sdt.create` method or sdt_ip item in `Sdt.add_sdt_ip` method.
    """

    def __init__(self, ip, role):
        params = utils.prepare_params(
            {
                "ip": ip,
                "role": role,
            },
            dump=False,
        )
        super(SdtIp, self).__init__(**params)


class SdtIpRoles:
    """SDT ip roles."""

    storage_only = "StorageOnly"
    host_only = "HostOnly"
    storage_and_host = "StorageAndHost"


class Sdt(base_client.EntityRequest):

    def send_post_request(self, url, action, entity, entity_id, params):
        """Send a POST request using pycurl.

        :param url: The base URL for the request.
        :param action: The action to perform.
        :param entity: The entity type.
        :param entity_id: The ID of the entity.
        :param params: The parameters to include in the request body.
        :return: A tuple of (HTTP status code, response body).
        """
        full_url = f"{url}/{action}/{entity}/{entity_id}"
        response_buffer = BytesIO()
        curl = pycurl.Curl()

        try:
            curl.setopt(pycurl.URL, full_url)
            curl.setopt(pycurl.POST, 1)
            if params:
                curl.setopt(pycurl.POSTFIELDS, utils.json_dumps(params))
            curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
            curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])

            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            response_body = response_buffer.getvalue().decode('utf-8')
        finally:
            curl.close()

        return status_code, response_body

    def add_ip(self, sdt_id, ip, role):
        """Add PowerFlex SDT target IP address.

        :type sdt_id: str
        :type ip: str
        :type role: str
        :rtype: dict
        """

        action = "addIp"

        params = dict(
            ip=ip,
            role=role,
        )

        status_code, response = self.send_post_request(
            self.base_action_url,
            action=action,
            entity=self.entity,
            entity_id=sdt_id,
            params=params,
        )
        if status_code != 200:  # Replaced requests.codes.ok with 200
            msg = (
                "Failed to add IP for PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    def remove_ip(self, sdt_id, ip):
        """Remove PowerFlex SDT target IP address.

        :type sdt_id: str
        :type ip: str
        :rtype: dict
        """

        action = "removeIp"

        params = dict(ip=ip)

        status_code, response = self.send_post_request(
            self.base_action_url,
            action=action,
            entity=self.entity,
            entity_id=sdt_id,
            params=params,
        )
        if status_code != 200:  # Replaced requests.codes.ok with 200
            msg = (
                "Failed to remove IP from PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    # Other methods (e.g., set_ip_role, set_storage_port, etc.) would follow the same pattern
    def set_ip_role(self, sdt_id, ip, role):
        """Set PowerFlex SDT target IP address role.

        :type sdt_id: str
        :type ip: str
        :param role: one of predefined attributes of SdtIpRoles
        :type role: str
        :rtype: dict
        """

        action = "modifyIpRole"

        params = dict(
            ip=ip,
            newRole=role,
        )

        r, response = self.send_post_request(
            self.base_action_url,
            action=action,
            entity=self.entity,
            entity_id=sdt_id,
            params=params,
        )
        if r.status_code != requests.codes.ok:
            msg = (
                "Failed to set ip role for PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    def set_storage_port(self, sdt_id, storage_port):
        """Set PowerFlex SDT storage port.

        :type sdt_id: str
        :type storage_port: int
        :rtype: dict
        """

        action = "modifyStoragePort"

        params = dict(newStoragePort=storage_port)

        r, response = self.send_post_request(
            self.base_action_url,
            action=action,
            entity=self.entity,
            entity_id=sdt_id,
            params=params,
        )
        if r.status_code != requests.codes.ok:
            msg = (
                "Failed to set storage port for PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    def set_nvme_port(self, sdt_id, nvme_port):
        """Set PowerFlex SDT NVMe port.

        :type sdt_id: str
        :type nvme_port: int
        :rtype: dict
        """

        action = "modifyNvmePort"

        params = dict(newNvmePort=nvme_port)

        r, response = self.send_post_request(
            self.base_action_url,
            action=action,
            entity=self.entity,
            entity_id=sdt_id,
            params=params,
        )
        if r.status_code != requests.codes.ok:
            msg = (
                "Failed to set nvme port for PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    def set_discovery_port(self, sdt_id, discovery_port):
        """Set PowerFlex SDT discovery port.

        :type sdt_id: str
        :type discovery_port: int
        :rtype: dict
        """

        action = "modifyDiscoveryPort"

        params = dict(newDiscoveryPort=discovery_port)

        r, response = self.send_post_request(
            self.base_action_url,
            action=action,
            entity=self.entity,
            entity_id=sdt_id,
            params=params,
        )
        if r.status_code != requests.codes.ok:
            msg = (
                "Failed to set discovery port for PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    def enter_maintenance_mode(self, sdt_id):
        """Enter Maintenance Mode.

        :type sdt_id: str
        :rtype: dict
        """

        action = "enterMaintenanceMode"

        r, response = self.send_post_request(
            self.base_action_url,
            action=action,
            entity=self.entity,
            entity_id=sdt_id,
            params=None,
        )
        if r.status_code != requests.codes.ok:
            msg = (
                "Failed to enter maintenance mode for PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    def exit_maintenance_mode(self, sdt_id):
        """Exit Maintenance Mode.

        :type sdt_id: str
        :rtype: dict
        """

        action = "exitMaintenanceMode"

        r, response = self.send_post_request(
            self.base_action_url,
            action=action,
            entity=self.entity,
            entity_id=sdt_id,
            params=None,
        )
        if r.status_code != requests.codes.ok:
            msg = (
                "Failed to exit maintenance mode for PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    def delete(self, sdt_id, force=None):
        """Remove PowerFlex SDT.

        :type sdt_id: str
        :type force: bool
        :rtype: None
        """

        params = dict(force=force)

        return self._delete_entity(sdt_id, params)
    # as add_ip and remove_ip, using the updated send_post_request method.