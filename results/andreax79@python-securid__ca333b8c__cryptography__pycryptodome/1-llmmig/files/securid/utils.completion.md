### Explanation of Changes

To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Cipher Initialization**:
   - The `Cipher` class from `cryptography.hazmat.primitives.ciphers` was replaced with the `AES` class from `Crypto.Cipher`.
   - The `modes.ECB()` mode from `cryptography` was replaced with the `AES.MODE_ECB` mode in `pycryptodome`.

2. **Encryptor and Decryptor**:
   - The `encryptor()` and `decryptor()` methods from `cryptography` were replaced with the `encrypt()` and `decrypt()` methods in `pycryptodome`.

3. **Imports**:
   - The `cryptography` imports were removed.
   - The `AES` class was imported from `Crypto.Cipher`.

4. **No Other Changes**:
   - The rest of the code, including function names, variable names, and logic, was left unchanged to ensure compatibility with the larger application.

---

### Modified Code

```python
#!/usr/bin/env python

from datetime import date, datetime
from typing import Optional, Union

from Crypto.Cipher import AES

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
    cipher = AES.new(bytes(key), AES.MODE_ECB)
    return cipher.encrypt(bytes(data))


def aes_ecb_decrypt(key: Bytes, data: Bytes) -> bytes:
    """
    Decrypt data with the key using AES-128 ECB
    """
    cipher = AES.new(bytes(key), AES.MODE_ECB)
    return cipher.decrypt(bytes(data))


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

---

### Summary of Changes
- Replaced `Cipher` and `modes.ECB()` from `cryptography` with `AES.new()` and `AES.MODE_ECB` from `pycryptodome`.
- Updated the encryption and decryption methods to use `encrypt()` and `decrypt()` from `pycryptodome`.
- Removed all imports from `cryptography` and replaced them with the appropriate `pycryptodome` imports.