from typing import List, Optional
from Crypto.PublicKey import RSA
from Crypto.IO import DER
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from .exceptions import InvalidCertificateChain
from .pem_cert_bytes_to_open_ssl_x509 import pem_cert_bytes_to_open_ssl_x509


def validate_certificate_chain(
    *,
    x5c: List[bytes],
    pem_root_certs_bytes: Optional[List[bytes]] = None,
) -> bool:
    """Validate that the certificates in x5c chain back to a known root certificate

    Args:
        `x5c`: X5C certificates from a registration response's attestation statement
        (optional) `pem_root_certs_bytes`: Any additional (PEM-formatted)
        root certificates that may complete the certificate chain

    Raises:
        `helpers.exceptions.InvalidCertificateChain` if chain cannot be validated
    """
    if pem_root_certs_bytes is None or len(pem_root_certs_bytes) < 1:
        # We have no root certs to chain back to, so just pass on validation
        return True

    # Make sure we have at least one certificate to try and link back to a root cert
    if len(x5c) < 1:
        raise InvalidCertificateChain("x5c was empty")

    # Prepare leaf cert
    try:
        leaf_cert_bytes = x5c[0]
        leaf_cert = RSA.import_key(DER.decode(leaf_cert_bytes))
    except Exception as err:
        raise InvalidCertificateChain(f"Could not prepare leaf cert: {err}")

    # Prepare any intermediate certs
    try:
        # May be an empty array, that's fine
        intermediate_certs_bytes = x5c[1:]
        intermediate_certs = [RSA.import_key(DER.decode(cert)) for cert in intermediate_certs_bytes]
    except Exception as err:
        raise InvalidCertificateChain(f"Could not prepare intermediate certs: {err}")

    # Prepare a collection of possible root certificates
    try:
        root_certs = [RSA.import_key(cert) for cert in pem_root_certs_bytes]
    except Exception as err:
        raise InvalidCertificateChain(f"Could not prepare root certs: {err}")

    # Validate the chain manually
    try:
        # Verify the leaf certificate against the intermediate certificates
        for i in range(len(intermediate_certs)):
            issuer_cert = intermediate_certs[i]
            subject_cert = leaf_cert if i == 0 else intermediate_certs[i - 1]

            # Verify the signature of the subject certificate using the issuer's public key
            signature = subject_cert._signature
            tbs_cert = subject_cert._tbs_certificate_bytes
            pkcs1_15.new(issuer_cert).verify(SHA256.new(tbs_cert), signature)

        # Verify the last intermediate certificate against the root certificates
        last_cert = intermediate_certs[-1] if intermediate_certs else leaf_cert
        for root_cert in root_certs:
            try:
                signature = last_cert._signature
                tbs_cert = last_cert._tbs_certificate_bytes
                pkcs1_15.new(root_cert).verify(SHA256.new(tbs_cert), signature)
                break
            except ValueError:
                continue
        else:
            raise InvalidCertificateChain("Certificate chain could not be validated against root certificates")
    except Exception as err:
        raise InvalidCertificateChain(f"Certificate chain validation failed: {err}")

    return True
