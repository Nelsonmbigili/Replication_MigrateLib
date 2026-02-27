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

from PyPowerFlex import exceptions
from PyPowerFlex.objects import sdt
import tests
import pytest


class TestSdtClient(tests.PyPowerFlexTestCase):
    async def setUp(self):
        super(TestSdtClient, self).setUp()
        await self.client.initialize()
        self.fake_sdt_id = "1"
        self.fake_sdt_name = "1"
        self.fake_pd_id = "1"
        self.fake_sdt_ips = [sdt.SdtIp("1.2.3.4", sdt.SdtIpRoles.storage_and_host)]

        self.MOCK_RESPONSES = {
            self.RESPONSE_MODE.Valid: {
                "/types/Sdt/instances": {"id": self.fake_sdt_id},
                "/instances/Sdt::{}".format(self.fake_sdt_id): {"id": self.fake_sdt_id},
                "/instances/Sdt::{}" "/action/addIp".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}" "/action/removeIp".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}" "/action/renameSdt".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}"
                "/action/modifyIpRole".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}"
                "/action/modifyStoragePort".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}"
                "/action/modifyNvmePort".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}"
                "/action/modifyDiscoveryPort".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}"
                "/action/enterMaintenanceMode".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}"
                "/action/exitMaintenanceMode".format(self.fake_sdt_id): {},
                "/instances/Sdt::{}" "/action/removeSdt".format(self.fake_sdt_id): {},
            },
            self.RESPONSE_MODE.Invalid: {
                "/types/Sdt/instances": {},
            },
        }

    @pytest.mark.asyncio
    async def test_sdt_create(self):
        await self.client.sdt.create(
            protection_domain_id=self.fake_pd_id,
            sdt_ips=self.fake_sdt_ips,
            sdt_name=self.fake_sdt_name,
        )

    def test_sdt_create_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexFailCreating,
                self.client.sdt.create,
                protection_domain_id=self.fake_pd_id,
                sdt_ips=self.fake_sdt_ips,
                sdt_name=self.fake_sdt_name,
            )

    def test_sdt_create_no_id_in_response(self):
        with self.http_response_mode(self.RESPONSE_MODE.Invalid):
            self.assertRaises(
                KeyError,
                self.client.sdt.create,
                protection_domain_id=self.fake_pd_id,
                sdt_ips=self.fake_sdt_ips,
                sdt_name=self.fake_sdt_name,
            )

    @pytest.mark.asyncio
    async def test_sdt_rename(self):
        await self.client.sdt.rename(self.fake_sdt_id, name="new_name")

    def test_sdt_rename_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexFailRenaming,
                self.client.sdt.rename,
                self.fake_sdt_id,
                name="new_name",
            )

    @pytest.mark.asyncio
    async def test_sdt_add_ip(self):
        await self.client.sdt.add_ip(
            self.fake_sdt_id, ip="1.2.3.4", role=sdt.SdtIpRoles.storage_and_host
        )

    def test_sdt_add_ip_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexClientException,
                self.client.sdt.add_ip,
                self.fake_sdt_id,
                ip="1.2.3.4",
                role=sdt.SdtIpRoles.storage_and_host,
            )

    @pytest.mark.asyncio
    async def test_sdt_remove_ip(self):
        await self.client.sdt.remove_ip(self.fake_sdt_id, ip="1.2.3.4")

    def test_sdt_remove_ip_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexClientException,
                self.client.sdt.remove_ip,
                self.fake_sdt_id,
                ip="1.2.3.4",
            )

    @pytest.mark.asyncio
    async def test_sdt_set_ip_role(self):
        await self.client.sdt.set_ip_role(
            self.fake_sdt_id, ip="1.2.3.4", role=sdt.SdtIpRoles.storage_and_host
        )

    def test_sdt_set_ip_role_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexClientException,
                self.client.sdt.set_ip_role,
                self.fake_sdt_id,
                ip="1.2.3.4",
                role=sdt.SdtIpRoles.storage_and_host,
            )

    @pytest.mark.asyncio
    async def test_sdt_set_storage_port(self):
        await self.client.sdt.set_storage_port(self.fake_sdt_id, storage_port=12200)

    def test_sdt_set_storage_port_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexClientException,
                self.client.sdt.set_storage_port,
                self.fake_sdt_id,
                storage_port=12200,
            )

    @pytest.mark.asyncio
    async def test_sdt_set_nvme_port(self):
        await self.client.sdt.set_nvme_port(self.fake_sdt_id, nvme_port=4420)

    def test_sdt_set_nvme_port_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexClientException,
                self.client.sdt.set_nvme_port,
                self.fake_sdt_id,
                nvme_port=4420,
            )

    @pytest.mark.asyncio
    async def test_sdt_set_discovery_port(self):
        await self.client.sdt.set_discovery_port(self.fake_sdt_id, discovery_port=8009)

    def test_sdt_set_discovery_port_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexClientException,
                self.client.sdt.set_discovery_port,
                self.fake_sdt_id,
                discovery_port=8009,
            )

    @pytest.mark.asyncio
    async def test_sdt_enter_maintenance_mode(self):
        await self.client.sdt.enter_maintenance_mode(self.fake_sdt_id)

    def test_sdt_enter_maintenance_mode_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexClientException,
                self.client.sdt.enter_maintenance_mode,
                self.fake_sdt_id,
            )

    @pytest.mark.asyncio
    async def test_sdt_exit_maintenance_mode(self):
        await self.client.sdt.exit_maintenance_mode(self.fake_sdt_id)

    def test_sdt_exit_maintenance_mode_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexClientException,
                self.client.sdt.exit_maintenance_mode,
                self.fake_sdt_id,
            )

    @pytest.mark.asyncio
    async def test_sdt_delete(self):
        await self.client.sdt.delete(self.fake_sdt_id)

    def test_sdt_delete_bad_status(self):
        with self.http_response_mode(self.RESPONSE_MODE.BadStatus):
            self.assertRaises(
                exceptions.PowerFlexFailDeleting,
                self.client.sdt.delete,
                self.fake_sdt_id,
            )
