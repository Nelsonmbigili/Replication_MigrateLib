### Explanation of Changes

To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Elliptic Curve Public Keys**:
   - The `EllipticCurvePublicNumbers` and `EllipticCurvePublicKey` classes from `cryptography` were replaced with the `ECC` class from `pycryptodome`.
   - The `ECC.construct()` method was used to create an elliptic curve public key using the `x`, `y` coordinates and the curve name.

2. **RSA Public Keys**:
   - The `RSAPublicNumbers` and `RSAPublicKey` classes from `cryptography` were replaced with the `RSA.construct()` method from `pycryptodome`.
   - The `RSA.construct()` method was used to create an RSA public key using the modulus (`n`) and exponent (`e`).

3. **Ed25519 Public Keys**:
   - The `Ed25519PublicKey.from_public_bytes()` method from `cryptography` was replaced with the `Ed25519PublicKey` class from `pycryptodome`.
   - The `Ed25519PublicKey` class in `pycryptodome` directly accepts the public key bytes.

4. **Backend Removal**:
   - The `default_backend()` function from `cryptography` was removed, as `pycryptodome` does not require a backend.

### Modified Code

```python
import codecs
from typing import Union

from Crypto.PublicKey import ECC, RSA
from Crypto.PublicKey.Ed25519 import Ed25519PublicKey

from .algorithms import get_ec2_curve
from .cose import COSECRV, COSEAlgorithmIdentifier
from .decode_credential_public_key import (
    DecodedEC2PublicKey,
    DecodedOKPPublicKey,
    DecodedRSAPublicKey,
)
from .exceptions import UnsupportedPublicKey


def decoded_public_key_to_cryptography(
    public_key: Union[DecodedOKPPublicKey, DecodedEC2PublicKey, DecodedRSAPublicKey]
) -> Union[Ed25519PublicKey, ECC.EccKey, RSA.RsaKey]:
    """Convert raw decoded public key parameters (crv, x, y, n, e, etc...) into
    public keys using primitives from the pycryptodome library
    """
    if isinstance(public_key, DecodedEC2PublicKey):
        """
        alg is -7 (ES256), where kty is 2 (with uncompressed points) and
        crv is 1 (P-256).
        https://www.w3.org/TR/webauthn-2/#sctn-public-key-easy
        """
        x = int(codecs.encode(public_key.x, "hex"), 16)
        y = int(codecs.encode(public_key.y, "hex"), 16)
        curve = get_ec2_curve(public_key.crv)

        ecc_pub_key = ECC.construct(curve=curve.name, point_x=x, point_y=y)

        return ecc_pub_key
    elif isinstance(public_key, DecodedRSAPublicKey):
        """
        alg is -257 (RS256)
        https://www.w3.org/TR/webauthn-2/#sctn-public-key-easy
        """
        e = int(codecs.encode(public_key.e, "hex"), 16)
        n = int(codecs.encode(public_key.n, "hex"), 16)

        rsa_pub_key = RSA.construct((n, e))

        return rsa_pub_key
    elif isinstance(public_key, DecodedOKPPublicKey):
        """
        -8 (EdDSA), where crv is 6 (Ed25519).
        https://www.w3.org/TR/webauthn-2/#sctn-public-key-easy
        """
        if public_key.alg != COSEAlgorithmIdentifier.EDDSA or public_key.crv != COSECRV.ED25519:
            raise UnsupportedPublicKey(
                f"OKP public key with alg {public_key.alg} and crv {public_key.crv} is not supported"
            )

        okp_pub_key = Ed25519PublicKey(public_key.x)

        return okp_pub_key
    else:
        raise UnsupportedPublicKey(f"Unrecognized decoded public key: {public_key}")
```

### Key Notes
- The `ECC.construct()` method requires the curve name, which is obtained from the `get_ec2_curve()` function. Ensure that this function returns the correct curve name as a string (e.g., `"P-256"`).
- The `Ed25519PublicKey` class in `pycryptodome` directly accepts the public key bytes, simplifying the migration for Ed25519 keys.
- The `pycryptodome` library does not use a backend, so all references to `default_backend()` were removed.