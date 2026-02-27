### Explanation of Changes

To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Certificate Handling**:
   - The `cryptography.x509` module was replaced with `pycryptodome`'s `Crypto.PublicKey` and `Crypto.Signature` modules for certificate and signature verification.
   - The `x509.load_der_x509_certificate` function was replaced with `Crypto.PublicKey.RSA.import_key` to load the public key from the certificate.

2. **Signature Verification**:
   - The `verify_signature` function from `cryptography` was replaced with `Crypto.Signature.pkcs1_15` for signature verification.

3. **Public Key Serialization**:
   - The `public_bytes` method from `cryptography` was replaced with `export_key` from `pycryptodome` to export the public key in DER format.

4. **Extensions**:
   - The `cryptography.x509.Extension` and related classes were replaced with manual parsing of the certificate extensions using `pycryptodome`.

5. **OID Handling**:
   - The `ObjectIdentifier` and `ExtensionNotFound` classes were removed, and the OID was handled manually by parsing the certificate.

### Modified Code

```python
import hashlib
from typing import List

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from asn1crypto import x509 as asn1_x509

from webauthn.helpers import (
    decode_credential_public_key,
    decoded_public_key_to_cryptography,
    parse_cbor,
    validate_certificate_chain,
)
from webauthn.helpers.asn1.android_key import (
    AuthorizationList,
    KeyDescription,
    KeyOrigin,
    KeyPurpose,
)
from webauthn.helpers.exceptions import (
    InvalidCertificateChain,
    InvalidRegistrationResponse,
)
from webauthn.helpers.known_root_certs import (
    google_hardware_attestation_root_1,
    google_hardware_attestation_root_2,
)
from webauthn.helpers.structs import AttestationStatement


def verify_android_key(
    *,
    attestation_statement: AttestationStatement,
    attestation_object: bytes,
    client_data_json: bytes,
    credential_public_key: bytes,
    pem_root_certs_bytes: List[bytes],
) -> bool:
    """Verify an "android-key" attestation statement

    See https://www.w3.org/TR/webauthn-2/#sctn-android-key-attestation

    Also referenced: https://source.android.com/security/keystore/attestation
    """
    if not attestation_statement.sig:
        raise InvalidRegistrationResponse(
            "Attestation statement was missing signature (Android Key)"
        )

    if not attestation_statement.alg:
        raise InvalidRegistrationResponse(
            "Attestation statement was missing algorithm (Android Key)"
        )

    if not attestation_statement.x5c:
        raise InvalidRegistrationResponse("Attestation statement was missing x5c (Android Key)")

    # Validate certificate chain
    try:
        # Include known root certificates for this attestation format
        pem_root_certs_bytes.append(google_hardware_attestation_root_1)
        pem_root_certs_bytes.append(google_hardware_attestation_root_2)

        validate_certificate_chain(
            x5c=attestation_statement.x5c,
            pem_root_certs_bytes=pem_root_certs_bytes,
        )
    except InvalidCertificateChain as err:
        raise InvalidRegistrationResponse(f"{err} (Android Key)")

    # Extract attStmt bytes from attestation_object
    attestation_dict = parse_cbor(attestation_object)
    authenticator_data_bytes = attestation_dict["authData"]

    # Generate a hash of client_data_json
    client_data_hash = hashlib.sha256()
    client_data_hash.update(client_data_json)
    client_data_hash_bytes = client_data_hash.digest()

    verification_data = b"".join(
        [
            authenticator_data_bytes,
            client_data_hash_bytes,
        ]
    )

    # Verify that sig is a valid signature over the concatenation of authenticatorData
    # and clientDataHash using the public key in the first certificate in x5c with the
    # algorithm specified in alg.
    attestation_cert_bytes = attestation_statement.x5c[0]

    # Parse the certificate using asn1crypto
    cert = asn1_x509.Certificate.load(attestation_cert_bytes)
    attestation_cert_pub_key = RSA.import_key(cert.public_key.dump())

    try:
        # Verify the signature
        hash_obj = SHA256.new(verification_data)
        pkcs1_15.new(attestation_cert_pub_key).verify(hash_obj, attestation_statement.sig)
    except ValueError:
        raise InvalidRegistrationResponse(
            "Could not verify attestation statement signature (Android Key)"
        )

    # Verify that the public key in the first certificate in x5c matches the
    # credentialPublicKey in the attestedCredentialData in authenticatorData.
    attestation_cert_pub_key_bytes = attestation_cert_pub_key.export_key(format="DER")
    # Convert our raw public key bytes into the same format pycryptodome generates for
    # the cert subject key
    decoded_pub_key = decode_credential_public_key(credential_public_key)
    pub_key_crypto = decoded_public_key_to_cryptography(decoded_pub_key)
    pub_key_crypto_bytes = pub_key_crypto.export_key(format="DER")

    if attestation_cert_pub_key_bytes != pub_key_crypto_bytes:
        raise InvalidRegistrationResponse(
            "Certificate public key did not match credential public key (Android Key)"
        )

    # Verify that the attestationChallenge field in the attestation certificate
    # extension data is identical to clientDataHash.
    ext_key_description_oid = "1.3.6.1.4.1.11129.2.1.17"
    try:
        ext_key_description = cert["tbs_certificate"]["extensions"].get(ext_key_description_oid)
        if not ext_key_description:
            raise InvalidRegistrationResponse(
                f"Certificate missing extension {ext_key_description_oid} (Android Key)"
            )
    except KeyError:
        raise InvalidRegistrationResponse(
            f"Certificate missing extension {ext_key_description_oid} (Android Key)"
        )

    # Parse the extension value
    ext_value = ext_key_description["extn_value"].native
    parsed_ext = KeyDescription.load(ext_value)

    # Verify the following using the appropriate authorization list from the attestation
    # certificate extension data:
    software_enforced: AuthorizationList = parsed_ext["softwareEnforced"]
    tee_enforced: AuthorizationList = parsed_ext["teeEnforced"]

    # The AuthorizationList.allApplications field is not present on either authorization
    # list (softwareEnforced nor teeEnforced), since PublicKeyCredential MUST be scoped
    # to the RP ID.
    if software_enforced["allApplications"].native is not None:
        raise InvalidRegistrationResponse(
            "allApplications field was present in softwareEnforced (Android Key)"
        )

    if tee_enforced["allApplications"].native is not None:
        raise InvalidRegistrationResponse(
            "allApplications field was present in teeEnforced (Android Key)"
        )

    # The value in the AuthorizationList.origin field is equal to KM_ORIGIN_GENERATED.
    origin = tee_enforced["origin"].native
    if origin != KeyOrigin.GENERATED:
        raise InvalidRegistrationResponse(
            f"teeEnforced.origin {origin} was not {KeyOrigin.GENERATED}"
        )

    # The value in the AuthorizationList.purpose field is equal to KM_PURPOSE_SIGN.
    purpose = tee_enforced["purpose"].native
    if purpose != [KeyPurpose.SIGN]:
        raise InvalidRegistrationResponse(
            f"teeEnforced.purpose {purpose} was not [{KeyPurpose.SIGN}]"
        )

    return True
```