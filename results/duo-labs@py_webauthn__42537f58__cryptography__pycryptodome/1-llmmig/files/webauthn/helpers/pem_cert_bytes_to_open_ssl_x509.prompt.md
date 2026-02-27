The following Python code currently uses the library "cryptography" version 43.0.3.
Migrate this code to use the library "pycryptodome" version 3.22.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "cryptography" to "pycryptodome".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "cryptography" and "pycryptodome".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from OpenSSL.crypto import X509


def pem_cert_bytes_to_open_ssl_x509(cert: bytes) -> X509:
    """Convert PEM-formatted certificate bytes into an X509 instance usable for cert
    chain validation
    """
    cert_crypto = load_pem_x509_certificate(cert, default_backend())
    cert_openssl = X509().from_cryptography(cert_crypto)
    return cert_openssl

```