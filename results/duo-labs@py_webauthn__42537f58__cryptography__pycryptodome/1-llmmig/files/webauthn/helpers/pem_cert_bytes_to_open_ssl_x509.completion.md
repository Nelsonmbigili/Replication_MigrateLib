### Explanation of Changes:
The original code uses the `cryptography` library to load a PEM-formatted certificate and convert it into an OpenSSL `X509` object. The `pycryptodome` library does not provide direct support for X.509 certificate handling, so we need to use the `pycryptodome` library's `Crypto.PublicKey.RSA` module to parse the certificate and extract the public key. However, since the `pycryptodome` library does not have a direct equivalent for `OpenSSL.crypto.X509`, we need to adjust the approach to work with the `pycryptodome` library's capabilities.

In this migration:
1. The `cryptography` library's `load_pem_x509_certificate` function is replaced with `pycryptodome`'s `Crypto.PublicKey.RSA.import_key` to parse the PEM certificate.
2. The `OpenSSL.crypto.X509` object creation is removed because `pycryptodome` does not provide an equivalent for this functionality. If the application requires OpenSSL's `X509` object, you may need to use a different library (e.g., `pyOpenSSL`) alongside `pycryptodome`.

### Modified Code:
```python
from Crypto.PublicKey import RSA


def pem_cert_bytes_to_open_ssl_x509(cert: bytes):
    """Convert PEM-formatted certificate bytes into an RSA public key instance."""
    try:
        cert_key = RSA.import_key(cert)
        return cert_key
    except ValueError as e:
        raise ValueError("Invalid PEM certificate format") from e
```

### Key Notes:
- The function now returns an RSA public key object instead of an OpenSSL `X509` object. If the application depends on the `X509` object, you may need to use a library like `pyOpenSSL` in addition to `pycryptodome`.
- The `RSA.import_key` function is used to parse the PEM certificate and extract the public key.
- Error handling is added to raise a `ValueError` if the provided certificate is not in a valid PEM format.