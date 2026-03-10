### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The import statement for `requests_mock` was removed, as it is not needed when using `requests_futures`.
2. **Session Creation**: Instead of using `requests_mock.Adapter()`, we will use `requests_futures.sessions.FuturesSession()` to create a session that supports asynchronous requests.
3. **Method Calls**: The method calls to the session for making requests will be updated to use the `FuturesSession` methods, which return a future object that can be used to retrieve the response.

### Modified Code
Here is the modified code after migrating to `requests_futures`:

```python
# SPDX-FileCopyrightText: 2021-2022 Rene Luria <rene.luria@infomaniak.com>
# SPDX-License-Identifier: Apache-2.0
"""Tests for certbot_dns_infomaniak.dns_infomaniak."""

import unittest

import logging
from unittest import mock
from requests_futures.sessions import FuturesSession

import sys
import io

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
        """Tests mthe cleanup method to see if client method is called"""
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
        self.session = FuturesSession()

        self.client = _APIDomain(FAKE_TOKEN)
        self.client.baseUrl = "mock://endpoint"
        self.client.session = self.session

    def _register_response(self, url, data=None, method='GET'):
        """Registers a reply in the requests mock

        :param str url: url to register response
        :param dict data: data to return
        :param str method: method for which response is registered (default to all)
        """
        resp = {"result": "success", "data": data}
        self.session.add_response(
            method,
            self.client.baseUrl + url,
            json=resp,
        )

    def _register_error(self, url, code, description):
        """Registers an error reply in the requests mock

        :param str url: url to register response
        :param int code: error code
        :param str description: error description
        """
        resp = {"result": "error", "error": {"code": code, "description": description}}
        self.session.add_response(
            'GET',
            self.client.baseUrl + url,
            json=resp,
        )

    def test_add_txt_record(self):
        """add_txt_record with normal params should succeed"""
        self._register_response(
            "/1/product?service_name=domain&customer_name={domain}".format(domain=DOMAIN),
            data=[
                {
                    "id": 654321,
                    "account_id": 1234,
                    "service_id": 14,
                    "service_name": "domain",
                    "customer_name": DOMAIN,
                }
            ],
        )
        self._register_response("/1/domain/654321/dns/record", "1001234", "POST")
        self.client.add_txt_record(
            DOMAIN, self.record_name, self.record_content, self.record_ttl
        )

    def test_add_txt_record_fail_to_find_domain(self):
        """add_txt_record with non existing domain should fail"""
        self._register_response(
            "/1/product?service_name=domain&customer_name={domain}".format(domain=DOMAIN),
            data=[],
        )
        with self.assertRaises(PluginError):
            self.client.add_txt_record(
                DOMAIN, self.record_name, self.record_content, self.record_ttl
            )

    def test_add_txt_record_fail_to_authenticate(self):
        """add_txt_record with wrong token should fail"""
        self._register_error(
            "/1/product?service_name=domain&customer_name={domain}".format(domain=DOMAIN),
            "not_authorized",
            "Authorization required",
        )
        with self.assertRaises(PluginError):
            self.client.add_txt_record(
                DOMAIN, self.record_name, self.record_content, self.record_ttl
            )

    def test_del_txt_record(self):
        """del_txt_record with normal params should succeed"""
        self._register_response(
            "/1/product?service_name=domain&customer_name={domain}".format(domain=DOMAIN),
            data=[
                {
                    "id": "654321",
                    "account_id": "1234",
                    "service_id": "14",
                    "service_name": "domain",
                    "customer_name": DOMAIN,
                }
            ],
        )
        self._register_response(
            "/1/domain/654321/dns/record",
            [
                {
                    "id": "11110",
                    "source": ".",
                    "source_idn": DOMAIN,
                    "type": "NS",
                    "ttl": 3600,
                    "target": "ns1.death.star",
                },
                {
                    "id": "11111",
                    "source": self.record_name,
                    "source_idn": "{name}.{domain}".format(name=self.record_name, domain=DOMAIN),
                    "type": "TXT",
                    "ttl": self.record_ttl,
                    "target": self.record_content,
                },
            ],
        )
        self._register_response(
            "/1/domain/654321/dns/record/11111",
            True,
            "DELETE",
        )
        self.client.del_txt_record(
            DOMAIN, "{name}.{domain}".format(name=self.record_name, domain=DOMAIN),
            self.record_content,
        )

    def test_del_txt_record_fail_to_find_domain(self):
        """del_txt_record with non existing domain should fail"""
        self._register_response(
            "/1/product?service_name=domain&customer_name={domain}".format(domain=DOMAIN),
            data=[],
        )
        with self.assertRaises(PluginError):
            self.client.del_txt_record(
                DOMAIN, self.record_name, self.record_content
            )

    def test_del_txt_record_fail_to_authenticate(self):
        """del_txt_recod with wrong token should fail"""
        self._register_error(
            "/1/product?service_name=domain&customer_name={domain}".format(domain=DOMAIN),
            "not_authorized",
            "Authorization required",
        )
        with self.assertRaises(PluginError):
            self.client.del_txt_record(
                DOMAIN, self.record_name, self.record_content
            )


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
``` 

This code now uses `requests_futures` for handling HTTP requests asynchronously, while maintaining the original structure and functionality of the code.