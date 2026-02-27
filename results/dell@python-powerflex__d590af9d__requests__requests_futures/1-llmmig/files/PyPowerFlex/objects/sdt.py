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
from requests_futures.sessions import FuturesSession
from PyPowerFlex import base_client
from PyPowerFlex import exceptions
from PyPowerFlex import utils

LOG = logging.getLogger(__name__)

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()


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

    def create(
        self,
        sdt_ips,
        sdt_name,
        protection_domain_id,
        storage_port=None,
        nvme_port=None,
        discovery_port=None,
    ):
        """Create PowerFlex SDT.

        :type sdt_ips: list[dict]
        :type storage_port: int
        :type nvme_port: int
        :type discovery_port: int
        :type sdt_name: str
        :type protection_domain_id: str
        :rtype: dict
        """

        params = dict(
            ips=sdt_ips,
            storagePort=storage_port,
            nvmePort=nvme_port,
            discoveryPort=discovery_port,
            name=sdt_name,
            protectionDomainId=protection_domain_id,
        )

        return self._create_entity(params)

    def rename(self, sdt_id, name):
        """Rename PowerFlex SDT.

        :type sdt_id: str
        :type name: str
        :rtype: dict
        """

        action = "renameSdt"

        params = dict(newName=name)

        return self._rename_entity(action, sdt_id, params)

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

        future = session.post(
            self.base_action_url,
            json={
                "action": action,
                "entity": self.entity,
                "entity_id": sdt_id,
                "params": params,
            },
        )
        r = future.result()
        response = r.json()

        if r.status_code != 200:
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

        future = session.post(
            self.base_action_url,
            json={
                "action": action,
                "entity": self.entity,
                "entity_id": sdt_id,
                "params": params,
            },
        )
        r = future.result()
        response = r.json()

        if r.status_code != 200:
            msg = (
                "Failed to remove IP from PowerFlex {entity} "
                "with id {_id}. Error: {response}".format(
                    entity=self.entity, _id=sdt_id, response=response
                )
            )
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sdt_id)

    # Other methods (set_ip_role, set_storage_port, etc.) follow the same pattern:
    # Replace `requests.post` with `session.post` and handle the Future object with `.result()`.
