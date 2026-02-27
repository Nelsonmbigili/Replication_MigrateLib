### Explanation of Changes
To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Import Changes**:
   - Removed imports from `cryptography.hazmat.primitives.ciphers` and `cryptography.hazmat.backends`.
   - Added imports from `Crypto.Cipher` for AES encryption and decryption.

2. **Cipher Initialization**:
   - Replaced the `Cipher` class from `cryptography` with the `AES` class from `pycryptodome`.
   - Used `AES.new()` to create the cipher object, specifying the mode (e.g., `AES.MODE_CBC` or `AES.MODE_ECB`) and additional parameters like the initialization vector (`iv`) for CBC mode.

3. **Encryptor and Decryptor**:
   - Removed the use of `encryptor().update()` and `decryptor().update()` from `cryptography`.
   - Replaced them with `encrypt()` and `decrypt()` methods from `pycryptodome`.

4. **Backend Removal**:
   - The `backend` parameter is not required in `pycryptodome`, so it was removed.

5. **No Other Changes**:
   - The function names, parameters, and overall structure of the code remain unchanged to ensure compatibility with the larger application.

---

### Modified Code
Here is the complete code after migration to `pycryptodome`:

```python
from Crypto.Cipher import AES

__all__ = [
    "encrypt_aes_cbc",
    "encrypt_aes_ecb",
    "decrypt_aes_cbc",
    "decrypt_aes_ecb",
]


def encrypt_aes_cbc(key: bytes, iv: bytes, data: bytes) -> bytes:
    r"""Encrypt data using AES CBC algorithm.

    Parameters
    ----------
    key : bytes
        Binary AES key.
    iv : bytes
        Binary initial initialization vector for CBC.
        Has to be 16 bytes long.
    data : bytes
        Binary data to be encrypted.
        Has to be multiple of 16 bytes.

    Returns
    -------
    encrypted_data : bytes
        Binary encrypted data.

    Raises
    ------
    ValueError
        Data length must be multiple of AES block size 16.

    Examples
    --------
    >>> import psec
    >>> key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    >>> iv = bytes.fromhex("00000000000000000000000000000000")
    >>> data = bytes.fromhex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF") * 2
    >>> psec.aes.encrypt_aes_cbc(key, iv, data).hex().upper()
    '592373540AE1B202615E6D210D868A8C6593A91B63F201B28860C4DE39375EB4'
    """
    if len(data) < 16 or len(data) % 16 != 0:
        raise ValueError(
            f"Data length ({str(len(data))}) must be multiple of AES block size 16."
        )

    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(data)


def encrypt_aes_ecb(key: bytes, data: bytes) -> bytes:
    r"""Encrypt data using AES ECB algorithm.

    Parameters
    ----------
    key : bytes
        Binary AES key.
    data : bytes
        Binary data to be encrypted.
        Has to be multiple of 16 bytes.

    Returns
    -------
    encrypted_data : bytes
        Binary encrypted data.

    Raises
    ------
    ValueError
        Data length must be multiple of AES block size 16.

    Examples
    --------
    >>> import psec
    >>> key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    >>> iv = bytes.fromhex("00000000000000000000000000000000")
    >>> data = bytes.fromhex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF") * 2
    >>> psec.aes.encrypt_aes_ecb(key, data).hex().upper()
    '592373540AE1B202615E6D210D868A8C592373540AE1B202615E6D210D868A8C'
    """
    if len(data) < 16 or len(data) % 16 != 0:
        raise ValueError(
            f"Data length ({str(len(data))}) must be multiple of AES block size 16."
        )

    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(data)


def decrypt_aes_cbc(key: bytes, iv: bytes, data: bytes) -> bytes:
    r"""Decrypt data using AES CBC algorithm.

    Parameters
    ----------
    key : bytes
        Binary AES key.
    iv : bytes
        Binary initial initialization vector for CBC.
        Has to be 16 bytes long.
    data : bytes
        Binary data to be decrypted.
        Has to be multiple of 16 bytes.

    Returns
    -------
    decrypted_data : bytes
        Binary decrypted data.

    Raises
    ------
    ValueError
        Data length must be multiple of AES block size 16.

    Examples
    --------
    >>> import psec
    >>> key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    >>> iv = bytes.fromhex("00000000000000000000000000000000")
    >>> cipher_text = bytes.fromhex("592373540AE1B202615E6D210D868A8C6593A91B63F201B28860C4DE39375EB4")
    >>> psec.aes.decrypt_aes_cbc(key, iv, cipher_text).hex().upper()
    'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
    """
    if len(data) < 16 or len(data) % 16 != 0:
        raise ValueError(
            f"Data length ({str(len(data))}) must be multiple of AES block size 16."
        )

    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(data)


def decrypt_aes_ecb(key: bytes, data: bytes) -> bytes:
    r"""Decrypt data using AES ECB algorithm.

    Parameters
    ----------
    key : bytes
        Binary AES key.
    data : bytes
        Binary data to be decrypted.
        Has to be multiple of 16 bytes.

    Returns
    -------
    decrypted_data : bytes
        Binary decrypted data.

    Raises
    ------
    ValueError
        Data length must be multiple of AES block size 16.

    Examples
    --------
    >>> import psec
    >>> key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    >>> cipher_text = bytes.fromhex("592373540AE1B202615E6D210D868A8C592373540AE1B202615E6D210D868A8C")
    >>> psec.aes.decrypt_aes_ecb(key, cipher_text).hex().upper()
    'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
    """
    if len(data) < 16 or len(data) % 16 != 0:
        raise ValueError(
            f"Data length ({str(len(data))}) must be multiple of AES block size 16."
        )

    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(data)
```

This code now uses `pycryptodome` for AES encryption and decryption while maintaining the same functionality and interface as the original code.