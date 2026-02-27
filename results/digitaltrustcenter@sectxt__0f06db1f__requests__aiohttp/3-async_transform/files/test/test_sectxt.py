#
# SPDX-License-Identifier: EUPL-1.2
#
import pytest
import aiohttp
from datetime import date, timedelta
from unittest import IsolatedAsyncioTestCase
from sectxt import Parser, SecurityTXT
from aioresponses import aioresponses
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


class SecTxtTestCase(IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_valid_security_txt(self):
        with aioresponses() as m:
            expires = f"Expires: {(date.today() + timedelta(days=10)).isoformat()}T18:37:07z\n"
            byte_content = b'Contact: mailto:me@example.com\n' + bytes(expires, "utf-8")
            m.get(
                "https://example.com/.well-known/security.txt",
                headers={"content-type": "text/plain"},
                body=byte_content
            )
            m.get("https://example.com/security.txt", body=_signed_example)
            s = SecurityTXT("example.com")
            assert (await s.is_valid())

    @pytest.mark.asyncio
    async def test_not_correct_path(self):
        with aioresponses() as m:
            m.get(
                "https://example.com/.well-known/security.txt",
                exception=aiohttp.ClientConnectionError,
            )
            m.get("https://example.com/security.txt", body=_signed_example)
            s = SecurityTXT("example.com")
            if not any(d["code"] == "location" for d in s.errors):
                pytest.fail("location error code should be given")

    @pytest.mark.asyncio
    async def test_invalid_uri_scheme(self):
        with aioresponses() as m:
            m.get(
                "https://example.com/.well-known/security.txt",
                exception=aiohttp.ClientConnectionError,
            )
            m.get(
                "https://example.com/security.txt", exception=aiohttp.ClientConnectionError
            )
            m.get("http://example.com/.well-known/security.txt", body=_signed_example)
            s = SecurityTXT("example.com")
            if not any(d["code"] == "invalid_uri_scheme" for d in s.errors):
                pytest.fail("invalid_uri_scheme error code should be given")

    @pytest.mark.asyncio
    async def test_byte_order_mark(self):
        with aioresponses() as m:
            expires = f"Expires: {(date.today() + timedelta(days=10)).isoformat()}T18:37:07z\n"
            byte_content_with_bom = b'\xef\xbb\xbf\xef\xbb\xbfContact: mailto:me@example.com\n' \
                                    + expires.encode()
            m.get(
                "https://example.com/.well-known/security.txt",
                headers={"content-type": "text/plain"},
                body=byte_content_with_bom,
            )
            s = SecurityTXT("example.com")
            assert (not await s.is_valid())
            if not any(d["code"] == "bom_in_file" for d in s.errors):
                pytest.fail("bom_in_file error code should be given")

    @pytest.mark.asyncio
    async def test_local_file(self):
        # Create a text file to be used for the local test
        test_file_name = "test_security.txt"
        f = open(test_file_name, "w")
        f.write(_signed_example)
        f.close()
        cwd = os.getcwd()
        test_file_path = os.path.join(cwd, test_file_name)
        s = SecurityTXT(test_file_path, is_local=True)
        assert (await s.is_valid())

        # Remove the file after the test is done.
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
