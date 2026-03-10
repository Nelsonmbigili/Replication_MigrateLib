### Explanation of Changes
To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Key Generation**: The `cryptography` library's `Fernet` key generation and encryption/decryption methods were replaced with equivalent functionality from `pycryptodome`. The `Fernet` class is not available in `pycryptodome`, so we will use AES encryption instead.
2. **AES Encryption**: The `Fernet` encryption and decryption methods were replaced with AES encryption using `pycryptodome`. This involves creating a cipher object and using it to encrypt and decrypt data.
3. **Padding**: Since AES requires the plaintext to be a multiple of the block size, we added padding to the plaintext before encryption and removed it after decryption.
4. **Base64 Encoding**: The encrypted data is base64 encoded to ensure it can be easily stored or transmitted.

Here is the modified code:

```python
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256


class Crypto:
    def __init__(self, key: str):
        self.key = key

    def get_key(self) -> bytes:
        digest = SHA256.new()
        digest.update(self.key.encode())
        return digest.digest()  # Return the raw bytes of the SHA256 hash

    def encrypt(self, password: str) -> bytes:
        key = self.get_key()
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(password.encode(), AES.block_size))
        iv = cipher.iv
        return base64.b64encode(iv + ct_bytes)  # Prepend IV for decryption

    def decrypt_token(self, token: bytes | None) -> str | None:
        if not token:
            return None

        raw = base64.b64decode(token)
        iv = raw[:16]  # Extract the IV from the beginning
        ct = raw[16:]  # Extract the ciphertext
        key = self.get_key()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ct), AES.block_size)
        return decrypted.decode()
``` 

This code now uses `pycryptodome` for encryption and decryption while maintaining the original structure and functionality of the `Crypto` class.