import re
from typing import Optional

from Crypto.IO import PKCS12
from Crypto.IO.X509 import X509

from . import Rut, constants


def get_subject_rut_from_certificate_pfx(pfx_file_bytes: bytes, password: Optional[str]) -> Rut:
    """
    Return the Chilean RUT stored in a digital certificate.

    Original source URL: https://github.com/fyntex/fd-cl-data/blob/cfd5a716fb9b2cbd8a03fca1bacfd1b844b1337f/fd_cl_data/apps/sii_auth/models/sii_auth_credential.py#L701-L745  # noqa: E501

    :param pfx_file_bytes: Digital certificate in PKCS12 format
    :param password: (Optional) The password to use to decrypt the PKCS12 file
    """
    # Load the PKCS12 file
    pfx = PKCS12.load(pfx_file_bytes, password.encode() if password is not None else None)

    # Extract the private key, certificate, and additional certificates
    private_key = pfx.get_privatekey()
    x509_cert = pfx.get_certificate()
    additional_certs = pfx.get_ca_certificates()

    assert x509_cert is not None

    # Parse the certificate to extract extensions
    cert = X509.new(x509_cert)
    extensions = cert.get_extensions()

    # Search for the RUT in the certificate's extensions
    subject_alt_name_ext = None
    for ext in extensions:
        if ext.get_oid() == constants.SII_CERT_TITULAR_RUT_OID:
            subject_alt_name_ext = ext
            break

    if subject_alt_name_ext is None:
        raise Exception('Certificate has no RUT information')

    # Extract the RUT value
    try:
        results = [
            x.value
            for x in subject_alt_name_ext.get_values()
            if hasattr(x, 'type_id') and x.type_id == constants.SII_CERT_TITULAR_RUT_OID
        ]
    except AttributeError as exc:
        raise Exception(f'Malformed certificate extension: {subject_alt_name_ext.get_oid()}') from exc

    if not results:
        raise Exception('Certificate has no RUT information')
    elif len(results) > 1:
        raise Exception(f'len(results) == {len(results)}')

    subject_rut_raw: bytes = results[0]
    subject_rut_str = subject_rut_raw.decode('utf-8')

    # Regex to extract Chilean RUT formatted string
    rut_match = re.search(r'\b\d{1,8}-[0-9Kk]\b', subject_rut_str)

    if not rut_match:
        raise Exception('RUT format not found in certificate')

    subject_rut = rut_match.group(0)

    return Rut(subject_rut)
