import hashlib
from typing import List

import cbor2
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from webauthn.helpers import (
    decode_credential_public_key,
    decoded_public_key_to_cryptography,
    parse_cbor,
    validate_certificate_chain,
)
from webauthn.helpers.exceptions import (
    InvalidCertificateChain,
    InvalidRegistrationResponse,
)
from webauthn.helpers.known_root_certs import apple_webauthn_root_ca
from webauthn.helpers.structs import AttestationStatement


def verify_apple(
    *,
    attestation_statement: AttestationStatement,
    attestation_object: bytes,
    client_data_json: bytes,
    credential_public_key: bytes,
    pem_root_certs_bytes: List[bytes],
) -> bool:
    """
    https://www.w3.org/TR/webauthn-2/#sctn-apple-anonymous-attestation
    """

    if not attestation_statement.x5c:
        raise InvalidRegistrationResponse("Attestation statement was missing x5c (Apple)")

    # Validate the certificate chain
    try:
        # Include known root certificates for this attestation format
        pem_root_certs_bytes.append(apple_webauthn_root_ca)

        validate_certificate_chain(
            x5c=attestation_statement.x5c,
            pem_root_certs_bytes=pem_root_certs_bytes,
        )
    except InvalidCertificateChain as err:
        raise InvalidRegistrationResponse(f"{err} (Apple)")

    # Concatenate authenticatorData and clientDataHash to form nonceToHash.
    attestation_dict = parse_cbor(attestation_object)
    authenticator_data_bytes = attestation_dict["authData"]

    client_data_hash = SHA256.new(client_data_json)
    client_data_hash_bytes = client_data_hash.digest()

    nonce_to_hash = b"".join(
        [
            authenticator_data_bytes,
            client_data_hash_bytes,
        ]
    )

    # Perform SHA-256 hash of nonceToHash to produce nonce.
    nonce = SHA256.new(nonce_to_hash)
    nonce_bytes = nonce.digest()

    # Verify that nonce equals the value of the extension with
    # OID 1.2.840.113635.100.8.2 in credCert.
    attestation_cert_bytes = attestation_statement.x5c[0]
    attestation_cert = RSA.import_key(attestation_cert_bytes)
    
    # Assuming we can access the extension directly
    ext_value = attestation_cert.get_extension('1.2.840.113635.100.8.2').value

    if ext_value != nonce_bytes:
        raise InvalidRegistrationResponse("Certificate nonce was not expected value (Apple)")

    # Verify that the credential public key equals the Subject Public Key of credCert.
    attestation_cert_pub_key_bytes = attestation_cert.export_key(format='DER')
    
    # Convert our raw public key bytes into the same format cryptography generates for
    # the cert subject key
    decoded_pub_key = decode_credential_public_key(credential_public_key)
    pub_key_crypto = decoded_public_key_to_cryptography(decoded_pub_key)
    pub_key_crypto_bytes = pub_key_crypto.export_key(format='DER')

    if attestation_cert_pub_key_bytes != pub_key_crypto_bytes:
        raise InvalidRegistrationResponse(
            "Certificate public key did not match credential public key (Apple)"
        )

    return True
