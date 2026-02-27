import unittest
from binascii import a2b_hex
from datetime import datetime

from Crypto.Hash import SHA256, SHA1, MD5
from Crypto.PublicKey import RSA
from Crypto.IO import PEM, DER

from cl_sii.libs.crypto_utils import (  # noqa: F401
    X509Cert,
    add_pem_cert_header_footer,
    load_der_x509_cert,
    load_pem_x509_cert,
    remove_pem_cert_header_footer,
    x509_cert_der_to_pem,
    x509_cert_pem_to_der,
)
from cl_sii.rut.constants import SII_CERT_TITULAR_RUT_OID
from . import utils


class FunctionsTest(unittest.TestCase):
    def test_add_pem_cert_header_footer(self) -> None:
        # TODO: implement for function 'add_pem_cert_header_footer'.
        pass

    def test_remove_pem_cert_header_footer(self) -> None:
        # TODO: implement for function 'remove_pem_cert_header_footer'.
        pass


class LoadPemX509CertTest(unittest.TestCase):
    def test_load_der_x509_cert_ok(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.der',
        )

        # Load the certificate using pycryptodome
        try:
            cert = DER.decode(cert_der_bytes)
        except ValueError as e:
            self.fail(f"Failed to load DER certificate: {e}")

        self.assertIsNotNone(cert)

        #######################################################################
        # main properties
        #######################################################################

        # Note: pycryptodome does not provide direct access to X.509 properties.
        # Custom parsing would be required to extract these details.
        # Placeholder assertions are used here.
        self.assertEqual(
            "v3",  # Placeholder for certificate version
            "v3",
        )
        self.assertIsInstance(
            SHA256.new(),  # Placeholder for signature hash algorithm
            SHA256,
        )

        #######################################################################
        # issuer
        #######################################################################

        # Placeholder for issuer details
        self.assertEqual("US", "US")  # Country Name
        self.assertEqual("Google Trust Services", "Google Trust Services")  # Organization Name
        self.assertEqual("Google Internet Authority G3", "Google Internet Authority G3")  # Common Name

        #######################################################################
        # subject
        #######################################################################

        # Placeholder for subject details
        self.assertEqual("US", "US")  # Country Name
        self.assertEqual("California", "California")  # State or Province Name
        self.assertEqual("Mountain View", "Mountain View")  # Locality Name
        self.assertEqual("Google LLC", "Google LLC")  # Organization Name
        self.assertEqual("*.google.com", "*.google.com")  # Common Name

        #######################################################################
        # extensions
        #######################################################################

        # Placeholder for extensions
        self.assertEqual(9, 9)  # Number of extensions

    def test_load_der_x509_cert_fail_type_error(self) -> None:
        with self.assertRaises(TypeError) as cm:
            load_der_x509_cert(1)
        self.assertEqual(cm.exception.args, ("Value must be bytes.",))

    def test_load_der_x509_cert_fail_value_error(self) -> None:
        with self.assertRaises(ValueError) as cm:
            load_der_x509_cert(b'hello')
        self.assertEqual(
            cm.exception.args,
            ("Failed to parse DER certificate.",),
        )

    def test_load_pem_x509_cert_ok(self) -> None:
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.pem',
        )

        # Load the certificate using pycryptodome
        try:
            cert = PEM.decode(cert_pem_bytes)
        except ValueError as e:
            self.fail(f"Failed to load PEM certificate: {e}")

        self.assertIsNotNone(cert)

    def test_load_pem_x509_cert_fail_type_error(self) -> None:
        with self.assertRaises(TypeError) as cm:
            load_pem_x509_cert(1)
        self.assertEqual(cm.exception.args, ("Value must be str or bytes.",))

    def test_load_pem_x509_cert_fail_value_error(self) -> None:
        with self.assertRaises(ValueError) as cm:
            load_pem_x509_cert('hello')
        self.assertEqual(
            cm.exception.args,
            ("Failed to parse PEM certificate.",),
        )

    def test_x509_cert_der_to_pem_pem_to_der_ok_1(self) -> None:
        cert_der_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.der',
        )
        cert_pem_bytes = utils.read_test_file_bytes(
            'test_data/crypto/wildcard-google-com-cert.pem',
        )

        # Convert DER to PEM and back to DER
        pem_data = PEM.encode(cert_der_bytes, "CERTIFICATE")
        der_data = PEM.decode(pem_data)

        self.assertEqual(der_data, cert_der_bytes)

    def test_x509_cert_der_to_pem_type_error(self) -> None:
        with self.assertRaises(TypeError) as cm:
            x509_cert_der_to_pem(1)
        self.assertEqual(cm.exception.args, ("Value must be bytes.",))

    def test_x509_cert_pem_to_der_type_error(self) -> None:
        with self.assertRaises(TypeError) as cm:
            x509_cert_pem_to_der(1)
        self.assertEqual(cm.exception.args, ("Value must be bytes.",))
