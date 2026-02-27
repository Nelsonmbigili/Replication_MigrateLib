The following Python code currently uses the library "cryptography" version 44.0.2.
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
#!/usr/bin/env python

from datetime import date, datetime
from typing import Optional, Union

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:  # pragma: no cover
    from secrets import SystemRandom  # (Python >= 3.6) type: ignore
except ImportError:  # pragma: no cover
    from random import SystemRandom


__all__ = [
    "AES_BLOCK_SIZE",
    "AES_KEY_SIZE",
    "Bytes",
    "BytesStr",
    "random",
    "Bytearray",
    "aes_ecb_encrypt",
    "aes_ecb_decrypt",
    "xor_block",
    "cbc_hash",
    "fromisoformat",
]

AES_BLOCK_SIZE = 16
AES_KEY_SIZE = 16

Bytes = Union[bytes, bytearray, "Bytearray"]
BytesStr = Union[bytes, bytearray, str, "Bytearray"]


random = SystemRandom()


class Bytearray(bytearray):
    def arrayset(self, c: int, n: int, dest_offset: int = 0) -> None:
        self[dest_offset : dest_offset + n] = [c] * n

    def arraycpy(self, src: BytesStr, n: Optional[int] = None, dest_offset: int = 0) -> None:
        if isinstance(src, str):
            src = bytes(src, "ascii")
        if n is None:
            n = len(src)
        n = min(n, len(self) - dest_offset, len(src))
        self[dest_offset : dest_offset + n] = src[0:n]


def aes_ecb_encrypt(key: Bytes, data: Bytes) -> bytes:
    """
    Encrypt data with the key using AES-128 ECB
    """
    cipher = Cipher(algorithms.AES(bytes(key)), modes.ECB())
    encryptor = cipher.encryptor()  # type: ignore
    return encryptor.update(bytes(data))  # type: ignore


def aes_ecb_decrypt(key: Bytes, data: Bytes) -> bytes:
    """
    Decrypt data with the key using AES-128 ECB
    """
    cipher = Cipher(algorithms.AES(bytes(key)), modes.ECB())
    decryptor = cipher.decryptor()  # type: ignore
    return decryptor.update(bytes(data))  # type: ignore


def xor_block(a: Bytes, b: Bytes) -> bytes:
    return bytes(a[i] ^ (b[i] if i < len(b) else 0) for i in range(0, len(a)))


def cbc_hash(key: Bytes, iv: Bytes, data: Bytes) -> bytes:
    """
    Calculate cipher block chaining message authentication code
    """
    result = bytes(iv)
    while len(data) > 0:
        result = aes_ecb_encrypt(key, xor_block(result, data))
        data = data[AES_BLOCK_SIZE:]
    return bytes(result)


def fromisoformat(dt: str) -> date:
    """
    Convert a YYYY-MM-DD string into a date object
    """
    return datetime.strptime(dt, "%Y-%m-%d").date()

```