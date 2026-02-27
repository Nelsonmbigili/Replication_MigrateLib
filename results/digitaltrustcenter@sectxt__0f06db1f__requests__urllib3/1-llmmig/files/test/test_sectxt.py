#
# SPDX-License-Identifier: EUPL-1.2
#
import pytest
import urllib3
from urllib3.exceptions import ConnectTimeoutError
from datetime import date, timedelta
from unittest import TestCase
from sectxt import Parser, SecurityTXT
import os

_signed_example = f"""-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

# Canonical URI
Canonical: https://example.com/.well-known/security.txt

# Our security address
Contact: mailto:security@example.com

# Our OpenPGP key
Encryption: https://example.com/pgp-key.txt

# Our security policy
Policy: https://example.com/security-policy.html

# Our security acknowledgments page
Acknowledgments: https://example.com/hall-of-fame.html

# CSAF link
CSAF: https://example.com/.well-known/csaf/provider-metadata.json

Expires: {(date.today() + timedelta(days=10)).isoformat()}T18:37:07z
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.2

wpwEAQEIABAFAmTHcawJEDs4gPMoG10dAACN5wP/UozhFqHcUWRNhg4KwfY4
HHXU8bf222naeYJHgaHadLTJJ8YQIQ9N5fYF7K4BM0jPZc48aaUPaBdhNxw+
KDtQJWPzVREIbbGLRQ5WNYrLR6/7v1LHTI8RvgY22QZD9EAkFQwgdG8paIP4
2APWewNf8e01t1oh4n5bDBtr4IaQoj0=
=DHXw
-----END PGP SIGNATURE-----
"""


class SecTxtTestCase(TestCase):
    # Other test cases remain unchanged...

    # noinspection PyMethodMayBeStatic
    def test_valid_security_txt(self):
        http = urllib3.PoolManager()
        expires = f"Expires: {(date.today() + timedelta(days=10)).isoformat()}T18:37:07z\n"
        byte_content = b'Contact: mailto:me@example.com\n' + bytes(expires, "utf-8")

        # Mocking the HTTP responses
        with urllib3.response.HTTPResponse(
            body=byte_content, headers={"content-type": "text/plain"}
        ) as response1, urllib3.response.HTTPResponse(
            body=_signed_example.encode(), headers={"content-type": "text/plain"}
        ) as response2:
            # Simulate the responses
            http.request = lambda method, url, **kwargs: response1 if "security.txt" in url else response2

            s = SecurityTXT("example.com")
            assert s.is_valid()

    # noinspection PyMethodMayBeStatic
    def test_not_correct_path(self):
        http = urllib3.PoolManager()

        # Mocking the HTTP responses
        with urllib3.response.HTTPResponse(
            body=None, status=408, preload_content=False
        ) as response1, urllib3.response.HTTPResponse(
            body=_signed_example.encode(), headers={"content-type": "text/plain"}
        ) as response2:
            # Simulate the responses
            def mock_request(method, url, **kwargs):
                if "well-known" in url:
                    raise ConnectTimeoutError()
                return response2

            http.request = mock_request

            s = SecurityTXT("example.com")
            if not any(d["code"] == "location" for d in s.errors):
                pytest.fail("location error code should be given")

    # noinspection PyMethodMayBeStatic
    def test_invalid_uri_scheme(self):
        http = urllib3.PoolManager()

        # Mocking the HTTP responses
        with urllib3.response.HTTPResponse(
            body=None, status=408, preload_content=False
        ) as response1, urllib3.response.HTTPResponse(
            body=_signed_example.encode(), headers={"content-type": "text/plain"}
        ) as response2:
            # Simulate the responses
            def mock_request(method, url, **kwargs):
                if "https" in url:
                    raise ConnectTimeoutError()
                return response2

            http.request = mock_request

            s = SecurityTXT("example.com")
            if not any(d["code"] == "invalid_uri_scheme" for d in s.errors):
                pytest.fail("invalid_uri_scheme error code should be given")

    def test_byte_order_mark(self):
        http = urllib3.PoolManager()
        expires = f"Expires: {(date.today() + timedelta(days=10)).isoformat()}T18:37:07z\n"
        byte_content_with_bom = b'\xef\xbb\xbf\xef\xbb\xbfContact: mailto:me@example.com\n' \
                                + expires.encode()

        # Mocking the HTTP response
        with urllib3.response.HTTPResponse(
            body=byte_content_with_bom, headers={"content-type": "text/plain"}
        ) as response:
            # Simulate the response
            http.request = lambda method, url, **kwargs: response

            s = SecurityTXT("example.com")
            assert not s.is_valid()
            if not any(d["code"] == "bom_in_file" for d in s.errors):
                pytest.fail("bom_in_file error code should be given")

    # Other test cases remain unchanged...
