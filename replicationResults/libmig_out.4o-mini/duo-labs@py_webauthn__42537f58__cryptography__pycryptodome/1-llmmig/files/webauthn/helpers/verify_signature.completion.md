### Explanation of Changes

To migrate the code from using the `cryptography` library to the `pycryptodome` library, several changes were necessary:

1. **Import Statements**: The import paths for public key classes and signature verification methods have changed. In `pycryptodome`, the relevant classes and methods are located in different modules.
2. **Signature Verification**: The method for verifying signatures has a different interface in `pycryptodome`. The `verify` method is replaced with the `verify` method of the `PKCS1_v1_5` class for RSA keys, and the `Ed25519` verification is handled differently.
3. **Padding Schemes**: The padding schemes for RSA signatures are handled through specific classes in `pycryptodome`, such as `PKCS1_v1_5` and `PSS`.

Here is the modified code:

```python
from typing import Union

from Crypto.PublicKey import DSA, RSA, ECC
from Crypto.Signature import pkcs1_15, pss
from Crypto.Hash import SHA256
from Crypto.Signature import eddsa
from Crypto.PublicKey import ECC

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
        eddsa.Ed25519Key,
        DSA.DsaKey,
    ],
    signature_alg: COSEAlgorithmIdentifier,
    signature: bytes,
    data: bytes,
) -> None:
    """Verify a signature was signed with the private key corresponding to the provided
    public key.

    Args:
        `public_key`: A public key loaded via pycryptodome's `import_key`, etc...
        `signature_alg`: Algorithm ID used to sign the signature
        `signature`: Signature to verify
        `data`: Data signed by private key

    Raises:
        `webauthn.helpers.exceptions.UnsupportedAlgorithm` when the algorithm is not a recognized COSE algorithm ID
        `webauthn.helpers.exceptions.UnsupportedPublicKey` when the public key is not a valid EC2, RSA, or OKP certificate
        `ValueError` when the signature cannot be verified
    """
    if isinstance(public_key, ECC.EccKey):
        public_key.verify(signature, data, get_ec2_sig_alg(signature_alg))
    elif isinstance(public_key, RSA.RsaKey):
        if is_rsa_pkcs(signature_alg):
            pkcs1_15.new(public_key).verify(SHA256.new(data), signature)
        elif is_rsa_pss(signature_alg):
            rsa_alg = get_rsa_pss_sig_alg(signature_alg)
            verifier = pss.new(public_key)
            verifier.verify(SHA256.new(data), signature)
        else:
            raise UnsupportedAlgorithm(f"Unrecognized RSA signature alg {signature_alg}")
    elif isinstance(public_key, eddsa.Ed25519Key):
        public_key.verify(signature, data)
    else:
        raise UnsupportedPublicKey(
            f"Unsupported public key for signature verification: {public_key}"
        )
```

### Key Changes Summary
- Changed the import statements to use `pycryptodome` classes and methods.
- Adjusted the signature verification logic to align with `pycryptodome`'s API.
- Used `SHA256` for hashing the data before verification, as `pycryptodome` requires explicit hashing for RSA signatures.