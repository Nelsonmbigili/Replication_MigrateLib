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

# Initialize a PoolManager for HTTP requests
http = urllib3.PoolManager()


class DeviceTestMode:
    """SDS devices test modes."""

    test_only = 'testOnly'
    no_test = 'noTest'
    test_and_activate = 'testAndActivate'


class DrlMode:
    """SDS drl modes."""

    volatile = 'Volatile'
    nonvolatile = 'NonVolatile'


class SdsIpRoles:
    """SDS ip roles."""

    sds_only = 'sdsOnly'
    sdc_only = 'sdcOnly'
    all = 'all'


class PerformanceProfile:
    """SDS performance profiles."""

    highperformance = 'HighPerformance'
    compact = 'Compact'


class AccelerationDeviceInfo(dict):
    """PowerFlex acceleration device object.

    JSON-serializable, should be used as `acceleration_devices_info` list item
    in `Sds.create` method.
    """

    def __init__(self,
                 device_path,
                 accp_id,
                 device_name=None):
        params = utils.prepare_params(
            {
                'accelerationDevicePath': device_path,
                'accpId': accp_id,
                'accelerationDeviceName': device_name,
            },
            dump=False
        )
        super(AccelerationDeviceInfo, self).__init__(**params)


class DeviceInfo:
    """PowerFlex device object.

    JSON-serializable, should be used as `devices_info` list item
    in `Sds.create` method.
    """

    def __init__(self,
                 device_path,
                 storage_pool_id,
                 device_name=None,
                 media_type=None):
        params = utils.prepare_params(
            {
                'devicePath': device_path,
                'storagePoolId': storage_pool_id,
                'deviceName': device_name,
                'mediaType': media_type,
            },
            dump=False
        )
        super(DeviceInfo, self).__init__(**params)


class RfcacheDevice(dict):
    """PowerFlex Rfcache device object.

    JSON-serializable, should be used as `rfcache_devices_info` list item
    in `Sds.create` method.
    """

    def __init__(self, path, name):
        params = utils.prepare_params(
            {
                'path': path,
                'name': name,
            },
            dump=False
        )
        super(RfcacheDevice, self).__init__(**params)


class SdsIp(dict):
    """PowerFlex sds ip object.

    JSON-serializable, should be used as `sds_ips` list item
    in `Sds.create` method or sds_ip item in `Sds.add_sds_ip` method.
    """

    def __init__(self, ip, role):
        params = utils.prepare_params(
            {
                'ip': ip,
                'role': role,
            },
            dump=False
        )
        super(SdsIp, self).__init__(**params)


class Sds(base_client.EntityRequest):
    def add_ip(self, sds_id, sds_ip):
        """Add PowerFlex SDS IP-address.

        :type sds_id: str
        :type sds_ip: dict
        :rtype: dict
        """

        action = 'addSdsIp'

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=sds_id,
                                             params=sds_ip)
        if r.status != 200:  # Replaced requests.codes.ok with 200
            msg = ('Failed to add IP for PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=sds_id, response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sds_id)

    def remove_ip(self, sds_id, ip):
        """Remove PowerFlex SDS IP-address.

        :type sds_id: str
        :type ip: str
        :rtype: dict
        """

        action = 'removeSdsIp'

        params = dict(
            ip=ip
        )

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=sds_id,
                                             params=params)
        if r.status != 200:  # Replaced requests.codes.ok with 200
            msg = ('Failed to remove IP from PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=sds_id, response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sds_id)

    def set_ip_role(self, sds_id, ip, role, force=None):
        """Set PowerFlex SDS IP-address role.

        :type sds_id: str
        :type ip: str
        :param role: one of predefined attributes of SdsIpRoles
        :type role: str
        :type force: bool
        :rtype: dict
        """

        action = 'setSdsIpRole'

        params = dict(
            sdsIpToSet=ip,
            newRole=role,
            forceRoleModification=force

        )

        r, response = self.send_post_request(self.base_action_url,
                                             action=action,
                                             entity=self.entity,
                                             entity_id=sds_id,
                                             params=params)
        if r.status != 200:  # Replaced requests.codes.ok with 200
            msg = ('Failed to set ip role for PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=sds_id, response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sds_id)

    # Other methods remain unchanged, except for replacing `requests.codes.ok` with `200` where applicable.
