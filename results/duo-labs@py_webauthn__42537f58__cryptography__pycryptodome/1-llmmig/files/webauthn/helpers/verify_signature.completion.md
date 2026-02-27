### Explanation of Changes

To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Public Key Classes**:
   - The `cryptography` library provides specific classes for different types of public keys (e.g., `EllipticCurvePublicKey`, `RSAPublicKey`, etc.). In `pycryptodome`, these are replaced with classes from the `Crypto.PublicKey` module, such as `Crypto.PublicKey.RSA` and `Crypto.PublicKey.ECC`.

2. **Signature Verification**:
   - The `verify` method in `cryptography` is replaced with equivalent methods in `pycryptodome`. For example:
     - RSA signature verification uses `Crypto.Signature.pkcs1_15` for PKCS#1 v1.5 and `Crypto.Signature.pss` for PSS.
     - ECC signature verification uses `Crypto.Signature.DSS`.
     - Ed25519 signature verification uses `Crypto.PublicKey.Ed25519`.

3. **Algorithm Mapping**:
   - The `pycryptodome` library requires explicit use of hash algorithms from `Crypto.Hash` (e.g., `Crypto.Hash.SHA256`), which are passed to the signature verification methods.

4. **Unsupported Key Types**:
   - Some key types (e.g., `Ed448PublicKey`, `X25519PublicKey`, `X448PublicKey`) are not supported by `pycryptodome`. These cases are handled by raising the `UnsupportedPublicKey` exception.

5. **Imports**:
   - All imports from `cryptography` are replaced with equivalent imports from `pycryptodome`.

---

### Modified Code

```python
from typing import Union

from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import pkcs1_15, pss, DSS
from Crypto.Hash import SHA256, SHA384, SHA512
from Crypto.PublicKey import Ed25519

from .algorithms import (
    get_ec2_sig_alg,
    get_rsa_pkcs1_sig_alg,
    get_rsa_pss_sig_alg,
    is_rsa_pkcs,
    is_rsa_pss,
)
from .cose import COSEAlgorithmIdentifier
from .exceptions import UnsupportedAlgorithm, UnsupportedPublicKey


def verify_signature(
    *,
    public_key: Union[
        ECC.EccKey,
        RSA.RsaKey,
        Ed25519.Ed25519Key,
    ],
    signature_alg: COSEAlgorithmIdentifier,
    signature: bytes,
    data: bytes,
) -> None:
    """Verify a signature was signed with the private key corresponding to the provided
    public key.

    Args:
        `public_key`: A public key loaded via pycryptodome's `RSA.import_key`, `ECC.import_key`, etc...
        `signature_alg`: Algorithm ID used to sign the signature
        `signature`: Signature to verify
        `data`: Data signed by private key

    Raises:
        `webauthn.helpers.exceptions.UnsupportedAlgorithm` when the algorithm is not a recognized COSE algorithm ID
        `webauthn.helpers.exceptions.UnsupportedPublicKey` when the public key is not a valid EC2, RSA, or OKP certificate
        `ValueError` when the signature cannot be verified
    """
    if isinstance(public_key, ECC.EccKey):
        # ECC signature verification
        try:
            hash_alg = get_ec2_sig_alg(signature_alg)
            if hash_alg == SHA256:
                h = SHA256.new(data)
            elif hash_alg == SHA384:
                h = SHA384.new(data)
            elif hash_alg == SHA512:
                h = SHA512.new(data)
            else:
                raise UnsupportedAlgorithm(f"Unsupported hash algorithm for ECC: {hash_alg}")
            verifier = DSS.new(public_key, 'fips-186-3')
            verifier.verify(h, signature)
        except ValueError:
            raise ValueError("Invalid ECC signature")
    elif isinstance(public_key, RSA.RsaKey):
        # RSA signature verification
        if is_rsa_pkcs(signature_alg):
            try:
                hash_alg = get_rsa_pkcs1_sig_alg(signature_alg)
                if hash_alg == SHA256:
                    h = SHA256.new(data)
                elif hash_alg == SHA384:
                    h = SHA384.new(data)
                elif hash_alg == SHA512:
                    h = SHA512.new(data)
                else:
                    raise UnsupportedAlgorithm(f"Unsupported hash algorithm for RSA PKCS1: {hash_alg}")
                pkcs1_15.new(public_key).verify(h, signature)
            except ValueError:
                raise ValueError("Invalid RSA PKCS1 signature")
        elif is_rsa_pss(signature_alg):
            try:
                hash_alg = get_rsa_pss_sig_alg(signature_alg)
                if hash_alg == SHA256:
                    h = SHA256.new(data)
                elif hash_alg == SHA384:
                    h = SHA384.new(data)
                elif hash_alg == SHA512:
                    h = SHA512.new(data)
                else:
                    raise UnsupportedAlgorithm(f"Unsupported hash algorithm for RSA PSS: {hash_alg}")
                verifier = pss.new(public_key)
                verifier.verify(h, signature)
            except ValueError:
                raise ValueError("Invalid RSA PSS signature")
        else:
            raise UnsupportedAlgorithm(f"Unrecognized RSA signature alg {signature_alg}")
    elif isinstance(public_key, Ed25519.Ed25519Key):
        # Ed25519 signature verification
        try:
            public_key.verify(signature, data)
        except ValueError:
            raise ValueError("Invalid Ed25519 signature")
    else:
        raise UnsupportedPublicKey(
            f"Unsupported public key for signature verification: {public_key}"
        )
```

---

### Key Notes:
1. The `pycryptodome` library does not support `Ed448PublicKey`, `X25519PublicKey`, or `X448PublicKey`. These cases are now handled by raising the `UnsupportedPublicKey` exception.
2. The `get_ec2_sig_alg`, `get_rsa_pkcs1_sig_alg`, and `get_rsa_pss_sig_alg` functions are assumed to return the appropriate hash algorithm classes from `Crypto.Hash` (e.g., `SHA256`, `SHA384`, etc.).
3. The `ValueError` exception is raised when signature verification fails, as this is the standard exception in `pycryptodome`.