### Explanation of Changes:
To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:
1. **Cipher Initialization**: The `Cipher` class from `cryptography.hazmat.primitives.ciphers` was replaced with the `AES` class from `Crypto.Cipher`.
   - The `modes.ECB()` mode in `cryptography` was replaced with the `AES.MODE_ECB` mode in `pycryptodome`.
2. **Encryptor and Decryptor**: The `encryptor()` and `decryptor()` methods from `cryptography` were replaced with the `encrypt()` and `decrypt()` methods in `pycryptodome`.
   - The `update()` and `finalize()` methods were removed because `pycryptodome` processes the entire input in one step.
3. **Imports**: The `cryptography` imports were replaced with the appropriate `pycryptodome` imports.

### Modified Code:
```python
"""SamsungTV Encrypted."""

import binascii

from Crypto.Cipher import AES

from .command import SamsungTVEncryptedCommand


# Padding for the input string --not related to encryption itself.
class Padding:
    BLOCK_SIZE = 16  # Bytes

    @staticmethod
    def pad(text: str) -> str:
        return text + (Padding.BLOCK_SIZE - len(text) % Padding.BLOCK_SIZE) * chr(
            Padding.BLOCK_SIZE - len(text) % Padding.BLOCK_SIZE
        )

    @staticmethod
    def unpad(text: bytes) -> str:
        return text[: -ord(text[len(text) - 1 :])].decode()


class SamsungTVEncryptedSession:
    def __init__(self, token: str, session_id: str) -> None:
        self._token = binascii.unhexlify(token)
        self._session_id = session_id
        self._cipher = AES.new(self._token, AES.MODE_ECB)

    def _decrypt(self, enc: bytes) -> str:
        decrypted_data = self._cipher.decrypt(binascii.unhexlify(enc))
        return Padding.unpad(decrypted_data)

    def _encrypt(self, raw: str) -> bytes:
        padded_data = bytes(Padding.pad(raw), encoding="utf8")
        return self._cipher.encrypt(padded_data)

    def encrypt_command(self, command: SamsungTVEncryptedCommand) -> str:
        command_bytes = self._encrypt(command.get_payload())

        int_array = ",".join(list(map(str, command_bytes)))
        return (
            '5::/com.samsung.companion:{"name":"callCommon","args":[{"Session_Id":'
            + self._session_id
            + ',"body":"['
            + int_array
            + ']"}]}'
        )
```

### Key Changes in Detail:
1. **Cipher Initialization**:
   - Old: `Cipher(algorithms.AES(self._token), modes.ECB())`
   - New: `AES.new(self._token, AES.MODE_ECB)`

2. **Encryptor and Decryptor**:
   - Old:
     ```python
     encryptor = self._cipher.encryptor()
     encryptor.update(data) + encryptor.finalize()
     ```
   - New:
     ```python
     self._cipher.encrypt(data)
     ```

   - Similarly for decryption:
     - Old: `decryptor.update(data) + decryptor.finalize()`
     - New: `self._cipher.decrypt(data)`

3. **Imports**:
   - Old: `from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes`
   - New: `from Crypto.Cipher import AES`

These changes ensure the code now uses `pycryptodome` for encryption and decryption while maintaining the same functionality.