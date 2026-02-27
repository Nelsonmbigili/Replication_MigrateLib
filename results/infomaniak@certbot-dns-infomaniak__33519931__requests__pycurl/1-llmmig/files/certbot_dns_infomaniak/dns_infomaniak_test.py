# SPDX-License-Identifier: Apache-2.0
"""Tests for certbot_dns_infomaniak.dns_infomaniak."""

import unittest
import logging
from unittest import mock
import pycurl
import json
import sys
import io
from io import BytesIO

from certbot.errors import PluginError
try:
    import certbot.compat.os as os
except ImportError:
    import os
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

from certbot_dns_infomaniak.dns_infomaniak import _APIDomain

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

FAKE_TOKEN = "xxxx"


class AuthenticatorTest(
    test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest
):
    """Class to test the Authenticator class"""
    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        self.config = mock.MagicMock()

        os.environ["INFOMANIAK_API_TOKEN"] = FAKE_TOKEN

        from certbot_dns_infomaniak.dns_infomaniak import Authenticator
        self.auth = Authenticator(self.config, "infomaniak")

        self.mock_client = mock.MagicMock(default_propagation_seconds=15)

        self.auth._api_client = mock.MagicMock(return_value=self.mock_client)

        try:
            from certbot.display.util import notify  # noqa: F401
            notify_patch = mock.patch('certbot._internal.main.display_util.notify')
            self.mock_notify = notify_patch.start()
            self.addCleanup(notify_patch.stop)
            self.old_stdout = sys.stdout
            sys.stdout = io.StringIO()
        except ImportError:
            self.old_stdout = sys.stdout

    def tearDown(self):
        sys.stdout = self.old_stdout

    def test_perform(self):
        """Tests the perform function to see if client method is called"""
        self.auth.perform([self.achall])

        expected = [
            mock.call.add_txt_record(DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_cleanup(self):
        """Tests the cleanup method to see if client method is called"""
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [
            mock.call.del_txt_record(DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)


class APIDomainTest(unittest.TestCase):
    """Class to test the _APIDomain class"""
    record_name = "foo"
    record_content = "bar"
    record_ttl = 42

    def setUp(self):
        self.client = _APIDomain(FAKE_TOKEN)
        self.client.baseUrl = "http://mock.endpoint"

    def _make_request(self, url, method="GET", data=None):
        """Helper function to make a pycurl request and return the response."""
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, self.client.baseUrl + url)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.setopt(pycurl.HTTPHEADER, [
            f"Authorization: Bearer {FAKE_TOKEN}",
            "Content-Type: application/json"
        ])
        if method == "POST":
            curl.setopt(pycurl.POST, 1)
            if data:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(data))
        elif method == "DELETE":
            curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")
        curl.perform()
        curl.close()
        response_body = buffer.getvalue().decode('utf-8')
        return json.loads(response_body)

    def test_add_txt_record(self):
        """add_txt_record with normal params should succeed"""
        # Mock domain lookup
        domain_data = [
            {
                "id": 654321,
                "account_id": 1234,
                "service_id": 14,
                "service_name": "domain",
                "customer_name": DOMAIN,
            }
        ]
        self.client._make_request = mock.MagicMock(return_value={"result": "success", "data": domain_data})

        # Mock DNS record creation
        self.client._make_request = mock.MagicMock(return_value={"result": "success", "data": "1001234"})

        self.client.add_txt_record(
            DOMAIN, self.record_name, self.record_content, self.record_ttl
        )

    def test_add_txt_record_fail_to_find_domain(self):
        """add_txt_record with non existing domain should fail"""
        self.client._make_request = mock.MagicMock(return_value={"result": "success", "data": []})
        with self.assertRaises(PluginError):
            self.client.add_txt_record(
                DOMAIN, self.record_name, self.record_content, self.record_ttl
            )

    def test_add_txt_record_fail_to_authenticate(self):
        """add_txt_record with wrong token should fail"""
        self.client._make_request = mock.MagicMock(return_value={
            "result": "error",
            "error": {"code": "not_authorized", "description": "Authorization required"}
        })
        with self.assertRaises(PluginError):
            self.client.add_txt_record(
                DOMAIN, self.record_name, self.record_content, self.record_ttl
            )

    def test_del_txt_record(self):
        """del_txt_record with normal params should succeed"""
        # Mock domain lookup
        domain_data = [
            {
                "id": "654321",
                "account_id": "1234",
                "service_id": "14",
                "service_name": "domain",
                "customer_name": DOMAIN,
            }
        ]
        self.client._make_request = mock.MagicMock(return_value={"result": "success", "data": domain_data})

        # Mock DNS record deletion
        self.client._make_request = mock.MagicMock(return_value={"result": "success"})

        self.client.del_txt_record(
            DOMAIN, "{name}.{domain}".format(name=self.record_name, domain=DOMAIN),
            self.record_content,
        )

    def test_del_txt_record_fail_to_find_domain(self):
        """del_txt_record with non existing domain should fail"""
        self.client._make_request = mock.MagicMock(return_value={"result": "success", "data": []})
        with self.assertRaises(PluginError):
            self.client.del_txt_record(
                DOMAIN, self.record_name, self.record_content
            )

    def test_del_txt_record_fail_to_authenticate(self):
        """del_txt_record with wrong token should fail"""
        self.client._make_request = mock.MagicMock(return_value={
            "result": "error",
            "error": {"code": "not_authorized", "description": "Authorization required"}
        })
        with self.assertRaises(PluginError):
            self.client.del_txt_record(
                DOMAIN, self.record_name, self.record_content
            )


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
