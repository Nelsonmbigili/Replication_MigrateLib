### Explanation of Changes
The migration from the `cryptography` library to `pycryptodome` involves replacing the functionality provided by `cryptography` with equivalent functionality from `pycryptodome`. Specifically:
1. **Certificate Handling**: `cryptography.x509` and its related methods for loading and parsing certificates are replaced with `pycryptodome`'s `Crypto.PublicKey.ECC` and `Crypto.IO.DER` for handling elliptic curve public keys.
2. **Signature Verification**: The `verify_signature` function from `cryptography` is replaced with `pycryptodome`'s `Crypto.Signature.DSS` for verifying ECDSA signatures.
3. **Elliptic Curve Public Key Handling**: The `cryptography.hazmat.primitives.asymmetric.ec` module is replaced with `pycryptodome`'s `Crypto.PublicKey.ECC` for working with elliptic curve public keys.

Below is the modified code:

---

### Modified Code
```python
import hashlib
from typing import List

from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.IO import DER

from webauthn.helpers import (
    aaguid_to_string,
    validate_certificate_chain,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.decode_credential_public_key import (
    DecodedEC2PublicKey,
    decode_credential_public_key,
)
from webauthn.helpers.exceptions import (
    InvalidCertificateChain,
    InvalidRegistrationResponse,
)
from webauthn.helpers.structs import AttestationStatement


def verify_fido_u2f(
    *,
    attestation_statement: AttestationStatement,
    client_data_json: bytes,
    rp_id_hash: bytes,
    credential_id: bytes,
    credential_public_key: bytes,
    aaguid: bytes,
    pem_root_certs_bytes: List[bytes],
) -> bool:
    """Verify a "fido-u2f" attestation statement

    See https://www.w3.org/TR/webauthn-2/#sctn-fido-u2f-attestation
    """
    if not attestation_statement.sig:
        raise InvalidRegistrationResponse("Attestation statement was missing signature (FIDO-U2F)")

    if not attestation_statement.x5c:
        raise InvalidRegistrationResponse(
            "Attestation statement was missing certificate (FIDO-U2F)"
        )

    if len(attestation_statement.x5c) > 1:
        raise InvalidRegistrationResponse(
            "Attestation statement contained too many certificates (FIDO-U2F)"
        )

    # Validate the certificate chain
    try:
        validate_certificate_chain(
            x5c=attestation_statement.x5c,
            pem_root_certs_bytes=pem_root_certs_bytes,
        )
    except InvalidCertificateChain as err:
        raise InvalidRegistrationResponse(f"{err} (FIDO-U2F)")

    # FIDO spec requires AAGUID in U2F attestations to be all zeroes
    # See https://fidoalliance.org/specs/fido-v2.1-rd-20191217/fido-client-to-authenticator-protocol-v2.1-rd-20191217.html#u2f-authenticatorMakeCredential-interoperability
    actual_aaguid = aaguid_to_string(aaguid)
    expected_aaguid = "00000000-0000-0000-0000-000000000000"
    if actual_aaguid != expected_aaguid:
        raise InvalidRegistrationResponse(
            f"AAGUID {actual_aaguid} was not expected {expected_aaguid} (FIDO-U2F)"
        )

    # Get the public key from the leaf certificate
    leaf_cert_bytes = attestation_statement.x5c[0]
    try:
        leaf_cert = DER.decode(leaf_cert_bytes)
        leaf_cert_pub_key = ECC.import_key(leaf_cert[0].payload)
    except (ValueError, IndexError):
        raise InvalidRegistrationResponse("Failed to parse leaf certificate (FIDO-U2F)")

    # We need the cert's x and y points so make sure they exist
    if not isinstance(leaf_cert_pub_key, ECC.EccKey):
        raise InvalidRegistrationResponse("Leaf cert was not an EC2 certificate (FIDO-U2F)")

    if leaf_cert_pub_key.curve != "P-256":
        raise InvalidRegistrationResponse("Leaf cert did not use P-256 curve (FIDO-U2F)")

    decoded_public_key = decode_credential_public_key(credential_public_key)
    if not isinstance(decoded_public_key, DecodedEC2PublicKey):
        raise InvalidRegistrationResponse("Credential public key was not EC2 (FIDO-U2F)")

    # Convert the public key to "Raw ANSI X9.62 public key format"
    public_key_u2f = b"".join(
        [
            bytes([0x04]),
            decoded_public_key.x,
            decoded_public_key.y,
        ]
    )

    # Generate a hash of client_data_json
    client_data_hash = hashlib.sha256()
    client_data_hash.update(client_data_json)
    client_data_hash_bytes = client_data_hash.digest()

    # Prepare the signature base (called "verificationData" in the WebAuthn spec)
    verification_data = b"".join(
        [
            bytes([0x00]),
            rp_id_hash,
            client_data_hash_bytes,
            credential_id,
            public_key_u2f,
        ]
    )

    # Verify the signature
    try:
        verifier = DSS.new(leaf_cert_pub_key, "fips-186-3")
        hash_obj = SHA256.new(verification_data)
        verifier.verify(hash_obj, attestation_statement.sig)
    except ValueError:
        raise InvalidRegistrationResponse(
            "Could not verify attestation statement signature (FIDO-U2F)"
        )

    # If we make it to here we're all good
    return True
```

---

### Key Changes Summary:
1. Replaced `cryptography.x509` with `Crypto.IO.DER` for parsing certificates.
2. Replaced `cryptography.hazmat.primitives.asymmetric.ec` with `Crypto.PublicKey.ECC` for elliptic curve public key handling.
3. Replaced `verify_signature` with `Crypto.Signature.DSS` for ECDSA signature verification.
4. Adjusted error handling to align with `pycryptodome`'s APIs.