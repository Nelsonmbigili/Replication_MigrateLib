import hashlib
from typing import List

import cbor2
from Crypto.PublicKey import RSA
from Crypto.IO import DER
from Crypto.Util.asn1 import DerSequence, DerObjectId

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

    client_data_hash = hashlib.sha256()
    client_data_hash.update(client_data_json)
    client_data_hash_bytes = client_data_hash.digest()

    nonce_to_hash = b"".join(
        [
            authenticator_data_bytes,
            client_data_hash_bytes,
        ]
    )

    # Perform SHA-256 hash of nonceToHash to produce nonce.
    nonce = hashlib.sha256()
    nonce.update(nonce_to_hash)
    nonce_bytes = nonce.digest()

    # Verify that nonce equals the value of the extension with
    # OID 1.2.840.113635.100.8.2 in credCert.
    attestation_cert_bytes = attestation_statement.x5c[0]

    # Parse the DER-encoded certificate
    cert = DER.DerSequence()
    cert.decode(attestation_cert_bytes)

    # Extract the extensions from the certificate
    tbs_certificate = DER.DerSequence()
    tbs_certificate.decode(cert[0])  # The first element is the TBSCertificate
    extensions = tbs_certificate[-1]  # Extensions are the last element in TBSCertificate

    # Parse the extensions to find the OID 1.2.840.113635.100.8.2
    ext_1_2_840_113635_100_8_2_oid = "1.2.840.113635.100.8.2"
    nonce_extension_value = None
    extensions_sequence = DER.DerSequence()
    extensions_sequence.decode(extensions)

    for ext in extensions_sequence:
        ext_sequence = DER.DerSequence()
        ext_sequence.decode(ext)
        oid = DerObjectId()
        oid.decode(ext_sequence[0])  # The first element is the OID
        if oid.value == ext_1_2_840_113635_100_8_2_oid:
            # The second element is the extension value
            nonce_extension_value = ext_sequence[1]
            break

    if nonce_extension_value is None:
        raise InvalidRegistrationResponse(
            f"Certificate missing extension {ext_1_2_840_113635_100_8_2_oid} (Apple)"
        )

    # Ignore the first six ASN.1 structure bytes that define the nonce as an OCTET STRING
    ext_value = nonce_extension_value[6:]

    if ext_value != nonce_bytes:
        raise InvalidRegistrationResponse("Certificate nonce was not expected value (Apple)")

    # Verify that the credential public key equals the Subject Public Key of credCert.
    attestation_cert_pub_key = RSA.import_key(cert[1])  # The second element is the public key
    attestation_cert_pub_key_bytes = attestation_cert_pub_key.export_key(format="DER")

    # Convert our raw public key bytes into the same format pycryptodome generates for
    # the cert subject key
    decoded_pub_key = decode_credential_public_key(credential_public_key)
    pub_key_crypto = decoded_public_key_to_cryptography(decoded_pub_key)
    pub_key_crypto_bytes = pub_key_crypto.export_key(format="DER")

    if attestation_cert_pub_key_bytes != pub_key_crypto_bytes:
        raise InvalidRegistrationResponse(
            "Certificate public key did not match credential public key (Apple)"
        )

    return True
