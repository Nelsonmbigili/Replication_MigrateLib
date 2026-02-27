#
# SPDX-License-Identifier: EUPL-1.2
#
import pytest
import treq
from datetime import date, timedelta
from unittest import TestCase
from sectxt import Parser, SecurityTXT
from twisted.internet.defer import inlineCallbacks
from twisted.web.client import ResponseFailed
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
    # Other test cases remain unchanged

    @pytest.mark.asyncio
    async def test_valid_security_txt(self):
        expires = f"Expires: {(date.today() + timedelta(days=10)).isoformat()}T18:37:07z\n"
        byte_content = b'Contact: mailto:me@example.com\n' + bytes(expires, "utf-8")

        # Mocking the HTTP responses
        async def mock_get(url, **kwargs):
            if url == "https://example.com/.well-known/security.txt":
                return treq.testing.StubTreqResponse(
                    200, {"content-type": "text/plain"}, byte_content
                )
            elif url == "https://example.com/security.txt":
                return treq.testing.StubTreqResponse(200, {}, _signed_example.encode())
            raise ResponseFailed("Mocked URL not found")

        treq.get = mock_get  # Replace treq.get with the mock

        s = SecurityTXT("example.com")
        assert await s.is_valid()

    @pytest.mark.asyncio
    async def test_not_correct_path(self):
        async def mock_get(url, **kwargs):
            if url == "https://example.com/.well-known/security.txt":
                raise ResponseFailed("Connection timeout")
            elif url == "https://example.com/security.txt":
                return treq.testing.StubTreqResponse(200, {}, _signed_example.encode())
            raise ResponseFailed("Mocked URL not found")

        treq.get = mock_get  # Replace treq.get with the mock

        s = SecurityTXT("example.com")
        if not any(d["code"] == "location" for d in await s.errors):
            pytest.fail("location error code should be given")

    @pytest.mark.asyncio
    async def test_invalid_uri_scheme(self):
        async def mock_get(url, **kwargs):
            if url == "https://example.com/.well-known/security.txt":
                raise ResponseFailed("Connection timeout")
            elif url == "https://example.com/security.txt":
                raise ResponseFailed("Connection timeout")
            elif url == "http://example.com/.well-known/security.txt":
                return treq.testing.StubTreqResponse(200, {}, _signed_example.encode())
            raise ResponseFailed("Mocked URL not found")

        treq.get = mock_get  # Replace treq.get with the mock

        s = SecurityTXT("example.com")
        if not any(d["code"] == "invalid_uri_scheme" for d in await s.errors):
            pytest.fail("invalid_uri_scheme error code should be given")

    @pytest.mark.asyncio
    async def test_byte_order_mark(self):
        expires = f"Expires: {(date.today() + timedelta(days=10)).isoformat()}T18:37:07z\n"
        byte_content_with_bom = b'\xef\xbb\xbf\xef\xbb\xbfContact: mailto:me@example.com\n' \
                                + expires.encode()

        async def mock_get(url, **kwargs):
            if url == "https://example.com/.well-known/security.txt":
                return treq.testing.StubTreqResponse(
                    200, {"content-type": "text/plain"}, byte_content_with_bom
                )
            raise ResponseFailed("Mocked URL not found")

        treq.get = mock_get  # Replace treq.get with the mock

        s = SecurityTXT("example.com")
        assert not await s.is_valid()
        if not any(d["code"] == "bom_in_file" for d in await s.errors):
            pytest.fail("bom_in_file error code should be given")
