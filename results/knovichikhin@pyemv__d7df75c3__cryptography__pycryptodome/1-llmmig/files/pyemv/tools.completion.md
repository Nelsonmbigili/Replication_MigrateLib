### Explanation of Changes
The original code uses the `cryptography` library for cryptographic operations, specifically for Triple DES (3DES) encryption in CBC and ECB modes. To migrate to the `pycryptodome` library, the following changes were made:

1. **Import Changes**:
   - Removed imports from `cryptography.hazmat.primitives.ciphers` and `cryptography.hazmat.backends`.
   - Added imports from `Crypto.Cipher` for `DES3` (Triple DES).

2. **Cipher Initialization**:
   - Replaced the `cryptography` `Cipher` object with `DES3.new()` from `pycryptodome`.
   - Specified the mode using `DES3.MODE_CBC` or `DES3.MODE_ECB` instead of `cryptography`'s `modes.CBC()` or `modes.ECB()`.

3. **Backend Removal**:
   - The `backend` parameter used in `cryptography` is not required in `pycryptodome`.

4. **Encryptor Handling**:
   - Removed the `encryptor()` method call, as `pycryptodome` directly provides encryption and decryption methods (`encrypt()` and `decrypt()`).

5. **Key Validation**:
   - `pycryptodome` automatically validates the key length for Triple DES. No additional changes were required for this.

### Modified Code
Here is the complete code after migrating to `pycryptodome`:

```python
import sys as _sys
import typing as _typing

from Crypto.Cipher import DES3

__all__ = [
    "xor",
    "odd_parity",
    "adjust_key_parity",
    "key_check_digits",
    "encrypt_tdes_cbc",
    "encrypt_tdes_ecb",
]


def xor(data: bytes, key: bytes) -> bytes:
    r"""Apply "exclusive or" to two bytes instances.

    Many thanks:
    https://stackoverflow.com/a/29409299

    Parameters
    ----------
    data : bytes
        Data to be XOR'd
    key : bytes
        Bit mask used to XOR data

    Returns
    -------
    bytes
        Data XOR'd by key
    """
    key = key[: len(data)]
    int_var = int.from_bytes(data, _sys.byteorder)
    int_key = int.from_bytes(key, _sys.byteorder)
    int_enc = int_var ^ int_key
    return int_enc.to_bytes(len(data), _sys.byteorder)


def odd_parity(v: int) -> int:
    r"""Check integer parity.

    Many thanks: in_parallel
    http://p-nand-q.com/python/_algorithms/math/bit-parity.html

    Parameters
    ----------
    v : int
        Integer to check parity of

    Returns
    -------
    int
        0 = even parity (even number of bits enabled, e.g. 0, 3, 5)
        1 = odd parity (odd number of bits enabled, e.g. 1, 2, 4)
    """
    v ^= v >> 16
    v ^= v >> 8
    v ^= v >> 4
    v &= 0xF
    return (0x6996 >> v) & 1


def adjust_key_parity(key: _typing.Union[bytes, bytearray]) -> bytes:
    r"""Adjust DES key parity key.

    Parameters
    ----------
    key : bytes, bytearray
        Binary key to adjust for odd parity.

    Returns
    -------
    adjusted_key : bytes
        Binary key adjusted for odd parity.

    Examples
    --------
    >>> from pyemv import tools
    >>> key = bytes.fromhex("1A2B3C4D5F0A1B2C4D5F6A7B8C9D0F1A")
    >>> tools.adjust_key_parity(key).hex().upper()
    '1A2A3D4C5E0B1A2C4C5E6B7A8C9D0E1A'
    """
    adjusted_key = bytearray(key)

    for i, byte in enumerate(adjusted_key):
        if not odd_parity(byte):
            adjusted_key[i] ^= 1

    return bytes(adjusted_key)


def key_check_digits(key: bytes, length: int = 2) -> bytes:
    r"""Calculate Triple DES key check digits.

    Parameters
    ----------
    key : bytes
        Binary key to provide check digits for. Has to be a valid DES key.
    length : int, optional
        Number of key check digits bytes provided in the response (default 2).

    Returns
    -------
    check_digits : bytes
        Binary check digits (`length` bytes)

    Examples
    --------
    >>> from pyemv import tools
    >>> key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    >>> tools.key_check_digits(key).hex().upper()
    '08D7'
    """
    cipher = DES3.new(key, DES3.MODE_ECB)
    return cipher.encrypt(b"\x00\x00\x00\x00\x00\x00\x00\x00")[:length]


def encrypt_tdes_cbc(key: bytes, iv: bytes, data: bytes) -> bytes:
    r"""Encrypt data using Triple DES CBC algorithm.

    Parameters
    ----------
    key : bytes
        Binary Triple DES key. Has to be a valid DES key.
    iv : bytes
        Binary initial initialization vector for CBC.
    data : bytes
        Binary data to be encrypted.

    Returns
    -------
    encrypted_data : bytes
        Binary encrypted data.

    Examples
    --------
    >>> from pyemv.tools import encrypt_tdes_cbc
    >>> key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    >>> iv = bytes.fromhex("0000000000000000")
    >>> encrypt_tdes_cbc(key, iv, b"12345678").hex().upper()
    '41D2FFBA3CDC15FE'
    """
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    return cipher.encrypt(data)


def encrypt_tdes_ecb(key: bytes, data: bytes) -> bytes:
    r"""Encrypt data using Triple DES ECB algorithm.

    Parameters
    ----------
    key : bytes
        Binary Triple DES key. Has to be a valid DES key.
    data : bytes
        Binary data to be encrypted.

    Returns
    -------
    encrypted_data : bytes
        Binary encrypted data.

    Examples
    --------
    >>> from pyemv.tools import encrypt_tdes_ecb
    >>> key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    >>> encrypt_tdes_ecb(key, b"12345678").hex().upper()
    '41D2FFBA3CDC15FE'
    """
    cipher = DES3.new(key, DES3.MODE_ECB)
    return cipher.encrypt(data)
```

### Summary of Changes
- Replaced `cryptography` imports with `pycryptodome` imports.
- Used `DES3.new()` for Triple DES encryption with appropriate modes (`MODE_CBC` and `MODE_ECB`).
- Removed the `backend` parameter and `encryptor()` method calls.
- The rest of the code remains unchanged.