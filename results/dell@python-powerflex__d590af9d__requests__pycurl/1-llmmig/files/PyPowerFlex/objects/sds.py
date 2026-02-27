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
    def _send_post_request(self, url, params):
        """Helper method to send POST requests using pycurl."""
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDS, utils.json_dumps(params))
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        status_code = c.getinfo(pycurl.RESPONSE_CODE)
        c.close()
        response_body = buffer.getvalue().decode('utf-8')
        return status_code, response_body

    def add_ip(self, sds_id, sds_ip):
        """Add PowerFlex SDS IP-address.

        :type sds_id: str
        :type sds_ip: dict
        :rtype: dict
        """

        action = 'addSdsIp'
        url = f"{self.base_action_url}/{action}/{self.entity}/{sds_id}"

        status_code, response = self._send_post_request(url, sds_ip)
        if status_code != 200:
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
        url = f"{self.base_action_url}/{action}/{self.entity}/{sds_id}"

        params = dict(ip=ip)
        status_code, response = self._send_post_request(url, params)
        if status_code != 200:
            msg = ('Failed to remove IP from PowerFlex {entity} '
                   'with id {_id}. Error: {response}'
                   .format(entity=self.entity, _id=sds_id, response=response))
            LOG.error(msg)
            raise exceptions.PowerFlexClientException(msg)

        return self.get(entity_id=sds_id)

    # Other methods would follow the same pattern, replacing `requests` with `_send_post_request`.
