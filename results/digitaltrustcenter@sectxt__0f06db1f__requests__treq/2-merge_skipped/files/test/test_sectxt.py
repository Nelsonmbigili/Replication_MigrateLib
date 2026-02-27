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
    def test_missing_space(self):
        content = "Contact:mailto:me@example.com\n# Wow"
        p = Parser(content.encode())
        self.assertEqual(p._errors[0]["code"], "no_space")

    def test_missing_value(self):
        content = "Contact: \n# Wow"
        p = Parser(content.encode())
        self.assertEqual(p._errors[0]["code"], "empty_value")

    def test_no_https(self):
        content = "Contact: http://example.com/contact\n# Wow"
        p = Parser(content.encode())
        self.assertEqual(p._errors[0]["code"], "no_https")

    def test_no_uri(self):
        content = "Contact: me@example.com\n# Wow"
        p = Parser(content.encode())
        self.assertEqual(p._errors[0]["code"], "no_uri")

    def test_signed(self):
        p = Parser(_signed_example.encode())
        self.assertTrue(p.is_valid())

    def test_signed_invalid_pgp(self):
        # Remove required pgp signature header for pgp data error
        content = _signed_example.replace(
            "-----BEGIN PGP SIGNATURE-----", ""
        )
        p1 = Parser(content.encode())
        self.assertFalse(p1.is_valid())
        self.assertEqual(
            len([1 for r in p1._errors if r["code"] == "pgp_data_error"]), 1
        )
        # Add dash escaping within the pgp signature for pgp data error
        content = _signed_example.replace(
            "-----BEGIN PGP SIGNATURE-----", "-----BEGIN PGP SIGNATURE-----\n- \n"
        )
        p2 = Parser(content.encode())
        self.assertFalse(p2.is_valid())
        self.assertEqual(
            len([1 for r in p2._errors if r["code"] == "pgp_data_error"]), 1
        )
        # create an error in the pgp message by invalidating the base64 encoding of the signature
        content = _signed_example.replace(
            "wpwEAQEIABAFAmTHcawJEDs4gPMoG10dAACN5wP/UozhFqHcUWRNhg4KwfY4", "wpwEAQEIABAFAmTH"
        ).replace(
            "HHXU8bf222naeYJHgaHadLTJJ8YQIQ9N5fYF7K4BM0jPZc48aaUPaBdhNxw+", "HHXU8bf222naeYJHga"
        )
        p3 = Parser(content.encode())
        self.assertFalse(p3.is_valid())
        self.assertEqual(
            len([1 for r in p3._errors if r["code"] == "pgp_error"]), 1
        )

    def test_signed_no_canonical(self):
        content = _signed_example.replace(
            "Canonical: https://example.com/.well-known/security.txt", ""
        )
        p = Parser(content.encode())
        self.assertEqual(p._recommendations[0]["code"], "no_canonical")

    def test_signed_dash_escaped(self):
        content = _signed_example.replace("Expires", "- Expires")
        p = Parser(content.encode())
        self.assertTrue(p.is_valid())

    def test_pgp_signed_formatting(self):
        content = "\r\n" + _signed_example
        p = Parser(content.encode())
        self.assertFalse(p.is_valid())
        self.assertTrue(any(d["code"] == "signed_format_issue" for d in p.errors))

    def test_unknown_fields(self):
        # Define a security.txt that contains unknown fields (but is valid).
        # The fields Last-updated and Unknown, should be marked as unknown.
        content = (
            f"Expires: {(date.today() + timedelta(days=10)).isoformat()}"
            "T18:37:07z\n"
            "Contact: mailto:security@example.com\n"
            "Last-updated: {date.today().isoformat()}T12:00:00z\n"
            "Unknown: value\n"
            "Encryption: https://example.com/pgp-key.txt\n"
        )

        # By default, recommend that there are unknown fields.
        p = Parser(content.encode())
        self.assertTrue(p.is_valid())
        self.assertEqual(
            len([1 for r in p._notifications if r["code"] == "unknown_field"]), 2
        )

        # When turned off, there should be no unknown_field recommendations.
        p = Parser(content.encode(), recommend_unknown_fields=False)
        self.assertTrue(p.is_valid())
        self.assertEqual(
            len([1 for r in p._notifications if r["code"] == "unknown_field"]), 0
        )

    def test_no_line_separators(self):
        expire_date = (date.today() + timedelta(days=10)).isoformat()
        single_line_security_txt = (
            "Contact: mailto:security@example.com  Expires: "
            f"{expire_date}T18:37:07z  # All on a single line"
        )
        p_line_separator = Parser(single_line_security_txt.encode())
        self.assertFalse(p_line_separator.is_valid())
        self.assertEqual(
            len([1 for r in p_line_separator._errors if r["code"] == "no_line_separators"]), 1
        )
        line_length_4_no_carriage_feed = (
            "line 1\n"
            "line 2\n"
            "line 3\n"
            "Contact: mailto:security@example.com  Expires"
        )
        p_length_4 = Parser(line_length_4_no_carriage_feed.encode())
        self.assertFalse(p_length_4.is_valid())
        self.assertEqual(
            len([1 for r in p_length_4._errors if r["code"] == "no_line_separators"]), 1
        )
        self.assertEqual(
            [r["line"] for r in p_length_4._errors if r["code"] == "no_line_separators"], [4]
        )

    def test_csaf_https_uri(self):
        content = _signed_example.replace(
            "CSAF: https://example.com/.well-known/csaf/provider-metadata.json",
            "CSAF: http://example.com/.well-known/csaf/provider-metadata.json",
        )
        p = Parser(content.encode())
        self.assertFalse(p.is_valid())
        self.assertEqual(len([1 for r in p._errors if r["code"] == "no_https"]), 1)

    def test_csaf_provider_file(self):
        content = _signed_example.replace(
            "CSAF: https://example.com/.well-known/csaf/provider-metadata.json",
            "CSAF: https://example.com/.well-known/csaf/other_provider_name.json",
        )
        p = Parser(content.encode())
        self.assertFalse(p.is_valid())
        self.assertEqual(len([1 for r in p._errors if r["code"] == "no_csaf_file"]), 1)

    def test_multiple_csaf_notification(self):
        content = _signed_example.replace(
            "# CSAF link",
            "# CSAF link\n"
            "CSAF: https://example2.com/.well-known/csaf/provider-metadata.json",
        )
        p = Parser(content.encode())
        self.assertTrue(p.is_valid())
        self.assertEqual(
            len([1 for r in p._recommendations if r["code"] == "multiple_csaf_fields"]), 1
        )

    def test_multiple_signed_messages(self):
        content = _signed_example.replace(
            "-----BEGIN PGP SIGNATURE-----",
            "-----BEGIN PGP SIGNATURE-----\n-----BEGIN PGP SIGNATURE-----",
        )
        p = Parser(content.encode())
        self.assertFalse(p.is_valid())
        self.assertEqual(
            len([1 for r in p._errors if r["code"] == "pgp_data_error"]), 1
        )

    def test_contact_field_properties(self):
        content = _signed_example.replace(
            "Contact: mailto:security@example.com",
            "Contact: mailto:security@example.com\n"
            "Contact: mailto:security%2Buri%2Bencoded@example.com\n"
            "Contact: mailto:not_a_valid_email\n"
            "Contact: tel:+1-201-555-0123\n"
            "Contact: https://example.com/security-contact.html"
        )
        p = Parser(content.encode())
        self.assertTrue(p.is_valid())
        self.assertEqual("security@example.com", p.contact_email)
        self.assertTrue("security@example.com" in p.contact_emails)
        self.assertTrue("security%2Buri%2Bencoded@example.com" in p.contact_emails)
        self.assertFalse("not_a_valid_email" in p.contact_emails)
        self.assertEqual("security@example.com", p.contact_email)
        self.assertEqual("https://example.com/security-contact.html", p.contact_url)

    # noinspection PyMethodMayBeStatic
    def test_valid_security_txt(self):
        with Mocker() as m:
            expires = f"Expires: {(date.today() + timedelta(days=10)).isoformat()}T18:37:07z\n"
            byte_content = b'Contact: mailto:me@example.com\n' + bytes(expires, "utf-8")
            m.get(
                "https://example.com/.well-known/security.txt",
                headers={"content-type": "text/plain"},
                content=byte_content
            )
            m.get("https://example.com/security.txt", text=_signed_example)
            s = SecurityTXT("example.com")
            assert (s.is_valid())

    # noinspection PyMethodMayBeStatic
    def test_not_correct_path(self):
        with Mocker() as m:
            m.get(
                "https://example.com/.well-known/security.txt",
                exc=requests.exceptions.ConnectTimeout,
            )
            m.get("https://example.com/security.txt", text=_signed_example)
            s = SecurityTXT("example.com")
            if not any(d["code"] == "location" for d in s.errors):
                pytest.fail("location error code should be given")

    # noinspection PyMethodMayBeStatic
    def test_invalid_uri_scheme(self):
        with Mocker() as m:
            m.get(
                "https://example.com/.well-known/security.txt",
                exc=requests.exceptions.ConnectTimeout,
            )
            m.get(
                "https://example.com/security.txt", exc=requests.exceptions.ConnectTimeout
            )
            m.get("http://example.com/.well-known/security.txt", text=_signed_example)
            s = SecurityTXT("example.com")
            if not any(d["code"] == "invalid_uri_scheme" for d in s.errors):
                pytest.fail("invalid_uri_scheme error code should be given")

    def test_byte_order_mark_parser(self):
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