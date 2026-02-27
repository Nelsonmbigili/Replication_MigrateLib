The following Python code currently uses the library "cryptography" version 42.0.8.
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
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class Crypto:
    def __init__(self, key: str):
        self.key = key

    def get_key(self) -> bytes:
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(self.key.encode())
        return base64.urlsafe_b64encode(digest.finalize())

    def encrypt(self, password: str) -> bytes:
        fernet = Fernet(self.get_key())
        return fernet.encrypt(password.encode())

    def decrypt_token(self, token: bytes | None) -> str | None:
        if not token:
            return None

        fernet = Fernet(self.get_key())
        return fernet.decrypt(token).decode()

```