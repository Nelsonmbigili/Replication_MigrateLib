### Explanation of Changes:
To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:
1. **Cipher and Padding Imports**: Replaced imports from `cryptography.hazmat.primitives.ciphers` and `cryptography.hazmat.primitives.padding` with equivalent imports from `Crypto.Cipher` and `Crypto.Util.Padding` in `pycryptodome`.
2. **Cipher Initialization**: Updated the `Cipher` initialization to use `AES` from `Crypto.Cipher` instead of `Cipher` from `cryptography`.
3. **Padding/Unpadding**: Replaced the `PKCS7` padding/unpadding mechanism from `cryptography` with `pad` and `unpad` functions from `Crypto.Util.Padding`.
4. **AES Mode**: Updated the AES mode to use `AES.MODE_CBC` from `pycryptodome`.

These changes ensure that the decryption functionality works seamlessly with `pycryptodome` while maintaining the same behavior as the original code.

---

### Modified Code:
Below is the updated code with the necessary changes:

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64decode

def decrypt(encrypted_str: str, key_str: str) -> str:
    iv_str, ct_str = encrypted_str.split(".", 2)

    key = b64decode(key_str)
    iv = b64decode(iv_str)
    ct = b64decode(ct_str)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ct)

    # Unpad the decrypted data
    bytestring = unpad(decrypted, AES.block_size)

    return bytestring.decode("utf-8")
```

---

### Key Changes in the Code:
1. **Cipher Initialization**:
   - Replaced `Cipher(algorithms.AES128(key), modes.CBC(iv))` with `AES.new(key, AES.MODE_CBC, iv)`.

2. **Padding/Unpadding**:
   - Removed the `PKCS7` padding/unpadding mechanism from `cryptography` and replaced it with `unpad` from `Crypto.Util.Padding`.

3. **AES Block Size**:
   - Used `AES.block_size` for unpadding, which is equivalent to the block size used in AES encryption.

---

### Notes:
- The `pycryptodome` library is a drop-in replacement for `pycrypto` and provides a similar API for cryptographic operations.
- The updated code ensures compatibility with `pycryptodome` version 3.22.0 and maintains the same functionality as the original implementation.