### Explanation of Changes

To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Import Statements**: The import paths for elliptic curve algorithms and hash algorithms were changed to reflect the structure of the `pycryptodome` library.
   - The `ECDSA` and curve classes were replaced with their equivalents from `Crypto.PublicKey` and `Crypto.Hash`.
   - The hash algorithms were imported from `Crypto.Hash` instead of `cryptography.hazmat.primitives.hashes`.

2. **Signature Algorithm Creation**: The way to create signature algorithms using `ECDSA` and hash functions was adjusted to fit the `pycryptodome` API.

3. **Curve Representation**: The elliptic curves are represented differently in `pycryptodome`, so the corresponding classes were used.

4. **Exception Handling**: The exceptions remain unchanged as they are custom exceptions defined in the application.

Here is the modified code:

```python
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA1, SHA256, SHA384, SHA512
from Crypto.Signature import DSS

from .cose import COSECRV, COSEAlgorithmIdentifier
from .exceptions import UnsupportedAlgorithm, UnsupportedEC2Curve


def is_rsa_pkcs(alg_id: COSEAlgorithmIdentifier) -> bool:
    """Determine if the specified COSE algorithm ID denotes an RSA PKCSv1 public key"""
    return alg_id in (
        COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_1,
        COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
        COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_384,
        COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_512,
    )


def is_rsa_pss(alg_id: COSEAlgorithmIdentifier) -> bool:
    """Determine if the specified COSE algorithm ID denotes an RSA PSS public key"""
    return alg_id in (
        COSEAlgorithmIdentifier.RSASSA_PSS_SHA_256,
        COSEAlgorithmIdentifier.RSASSA_PSS_SHA_384,
        COSEAlgorithmIdentifier.RSASSA_PSS_SHA_512,
    )


def get_ec2_sig_alg(alg_id: COSEAlgorithmIdentifier):
    """Turn an "ECDSA" COSE algorithm identifier into a corresponding signature
    algorithm
    """
    if alg_id == COSEAlgorithmIdentifier.ECDSA_SHA_256:
        return DSS.new(ECC.generate(curve='P-256'), 'fips-186-3', SHA256)
    if alg_id == COSEAlgorithmIdentifier.ECDSA_SHA_512:
        return DSS.new(ECC.generate(curve='P-521'), 'fips-186-3', SHA512)

    raise UnsupportedAlgorithm(f"Unrecognized EC2 signature alg {alg_id}")


def get_ec2_curve(crv_id: COSECRV):
    """Turn an EC2 COSE crv identifier into a corresponding curve"""
    if crv_id == COSECRV.P256:
        return ECC.generate(curve='P-256')
    elif crv_id == COSECRV.P384:
        return ECC.generate(curve='P-384')
    elif crv_id == COSECRV.P521:
        return ECC.generate(curve='P-521')

    raise UnsupportedEC2Curve(f"Unrecognized EC2 curve {crv_id}")


def get_rsa_pkcs1_sig_alg(alg_id: COSEAlgorithmIdentifier):
    """Turn an "RSASSA_PKCS1" COSE algorithm identifier into a corresponding signature
    algorithm
    """
    if alg_id == COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_1:
        return SHA1
    if alg_id == COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256:
        return SHA256
    if alg_id == COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_384:
        return SHA384
    if alg_id == COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_512:
        return SHA512

    raise UnsupportedAlgorithm(f"Unrecognized RSA PKCS1 signature alg {alg_id}")


def get_rsa_pss_sig_alg(alg_id: COSEAlgorithmIdentifier):
    """Turn an "RSASSA_PSS" COSE algorithm identifier into a corresponding signature
    algorithm
    """
    if alg_id == COSEAlgorithmIdentifier.RSASSA_PSS_SHA_256:
        return SHA256
    if alg_id == COSEAlgorithmIdentifier.RSASSA_PSS_SHA_384:
        return SHA384
    if alg_id == COSEAlgorithmIdentifier.RSASSA_PSS_SHA_512:
        return SHA512

    raise UnsupportedAlgorithm(f"Unrecognized RSA PSS signature alg {alg_id}")
``` 

This code now uses the `pycryptodome` library while maintaining the original structure and functionality.