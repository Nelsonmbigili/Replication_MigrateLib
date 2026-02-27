### Explanation of Changes

To migrate the code from the `cryptography` library to the `pycryptodome` library, the following changes were made:

1. **Cipher Initialization**:
   - The `Cipher` class from `cryptography.hazmat.primitives.ciphers` was replaced with `Crypto.Cipher.AES` from `pycryptodome`.
   - The `encryptor()` and `decryptor()` methods were replaced with `encrypt()` and `decrypt()` methods, respectively.

2. **AES Modes**:
   - The `modes.CBC` from `cryptography` was replaced with `Crypto.Cipher.AES.MODE_CBC`.

3. **Key and IV Handling**:
   - The `pycryptodome` library requires the key and IV to be passed directly during the initialization of the `AES` cipher.

4. **Finalization**:
   - The `finalize()` method from `cryptography` was removed because `pycryptodome` does not require explicit finalization. The `encrypt()` and `decrypt()` methods handle the entire operation.

5. **Imports**:
   - Removed imports from `cryptography` and added imports from `pycryptodome`.

Below is the modified code.

---

### Modified Code

```python
"""SamsungTV Encrypted."""

import hashlib
import logging
import re
import struct
from typing import Dict, Optional

import aiohttp
from Crypto.Cipher import AES

LOGGER = logging.getLogger(__name__)
BLOCK_SIZE = 16
SHA_DIGEST_LENGTH = 20
PUBLIC_KEY = "2cb12bb2cbf7cec713c0fff7b59ae68a96784ae517f41d259a45d20556177c0ffe951ca60ec03a990c9412619d1bee30adc7773088c5721664cffcedacf6d251cb4b76e2fd7aef09b3ae9f9496ac8d94ed2b262eee37291c8b237e880cc7c021fb1be0881f3d0bffa4234d3b8e6a61530c00473ce169c025f47fcc001d9b8051"
PRIVATE_KEY = "2fd6334713816fae018cdee4656c5033a8d6b00e8eaea07b3624999242e96247112dcd019c4191f4643c3ce1605002b2e506e7f1d1ef8d9b8044e46d37c0d5263216a87cd783aa185490436c4a0cb2c524e15bc1bfeae703bcbc4b74a0540202e8d79cadaae85c6f9c218bc1107d1f5b4b9bd87160e782f4e436eeb17485ab4d"
WB_KEY = "abbb120c09e7114243d1fa0102163b27"
TRANS_KEY = "6c9474469ddf7578f3e5ad8a4c703d99"
PRIME = "b361eb0ab01c3439f2c16ffda7b05e3e320701ebee3e249123c3586765fd5bf6c1dfa88bb6bb5da3fde74737cd88b6a26c5ca31d81d18e3515533d08df619317063224cf0943a2f29a5fe60c1c31ddf28334ed76a6478a1122fb24c4a94c8711617ddfe90cf02e643cd82d4748d6d4a7ca2f47d88563aa2baf6482e124acd7dd"


def _encrypt_parameter_data_with_aes(data: bytes) -> bytes:
    iv = b"\x00" * BLOCK_SIZE
    output = b""
    for num in range(0, 128, 16):
        cipher = AES.new(bytes.fromhex(WB_KEY), AES.MODE_CBC, iv)
        output += cipher.encrypt(data[num : num + 16])

    return output


def _decrypt_parameter_data_with_aes(data: bytes) -> bytes:
    iv = b"\x00" * BLOCK_SIZE
    output = b""
    for num in range(0, 128, 16):
        cipher = AES.new(bytes.fromhex(WB_KEY), AES.MODE_CBC, iv)
        output += cipher.decrypt(data[num : num + 16])

    return output


def _generate_server_hello(user_id: str, pin: str) -> Dict[str, bytes]:
    sha1 = hashlib.sha1()
    sha1.update(pin.encode("utf-8"))
    pin_hash = sha1.digest()
    aes_key = pin_hash[:16]
    LOGGER.debug("AES key: %s", aes_key.hex())

    iv = b"\x00" * BLOCK_SIZE
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(bytes.fromhex(PUBLIC_KEY))
    LOGGER.debug("AES encrypted: %s", encrypted.hex())

    swapped = _encrypt_parameter_data_with_aes(encrypted)
    LOGGER.debug("AES swapped: %s", swapped.hex())

    data = struct.pack(">I", len(user_id)) + user_id.encode("utf-8") + swapped
    LOGGER.debug("data buffer: %s", data.hex().upper())

    sha1 = hashlib.sha1()
    sha1.update(data)
    data_hash = sha1.digest()
    LOGGER.debug("hash: %s", data_hash.hex())
    server_hello = (
        b"\x01\x02"
        + b"\x00" * 5
        + struct.pack(">I", len(user_id) + 132)
        + data
        + b"\x00" * 5
    )

    return {"serverHello": server_hello, "hash": data_hash, "AES_key": aes_key}


def _parse_client_hello(
    client_hello: str, data_hash: bytes, aes_key: bytes, user_id: str
) -> Optional[Dict[str, bytes]]:
    USER_ID_POS = 15
    USER_ID_LEN_POS = 11
    GX_SIZE = 0x80

    LOGGER.debug("hello: %s", client_hello)
    data = bytes.fromhex(client_hello)
    userIdLen = struct.unpack(">I", data[11:15])[0]
    thirdLen = userIdLen + 132
    LOGGER.debug("thirdLen: %s", str(thirdLen))

    dest = data[USER_ID_LEN_POS : thirdLen + USER_ID_LEN_POS] + data_hash
    LOGGER.debug("dest: %s", dest.hex())

    userId = data[USER_ID_POS : userIdLen + USER_ID_POS]
    LOGGER.debug("userId: %s", userId.decode("utf-8"))

    pEncWBGx = data[USER_ID_POS + userIdLen : GX_SIZE + USER_ID_POS + userIdLen]
    LOGGER.debug("pEncWBGx: %s", pEncWBGx.hex())

    pEncGx = _decrypt_parameter_data_with_aes(pEncWBGx)
    LOGGER.debug("pEncGx: %s", pEncGx.hex())

    iv = b"\x00" * BLOCK_SIZE
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    pGx = cipher.decrypt(pEncGx)
    LOGGER.debug("pGx: %s", pGx.hex())

    bnPGx = int(pGx.hex(), 16)
    bnPrime = int(PRIME, 16)
    bnPrivateKey = int(PRIVATE_KEY, 16)
    secret = bytes.fromhex(
        hex(pow(bnPGx, bnPrivateKey, bnPrime)).rstrip("L").lstrip("0x")
    )
    LOGGER.debug("secret: %s", secret.hex())

    dataHash2 = data[
        USER_ID_POS
        + userIdLen
        + GX_SIZE : USER_ID_POS
        + userIdLen
        + GX_SIZE
        + SHA_DIGEST_LENGTH
    ]  # fmt: skip
    LOGGER.debug("hash2: %s", dataHash2.hex())

    secret2 = userId + secret
    LOGGER.debug("secret2: %s", secret2.hex())

    sha1 = hashlib.sha1()
    sha1.update(secret2)
    dataHash3 = sha1.digest()
    LOGGER.debug("hash3: %s", dataHash3.hex())
    if dataHash2 != dataHash3:
        LOGGER.error("Pin error!!!")
        return None

    LOGGER.info("Pin OK")
    flagPos = userIdLen + USER_ID_POS + GX_SIZE + SHA_DIGEST_LENGTH
    if ord(data[flagPos : flagPos + 1]):
        LOGGER.error("First flag error!!!")
        return None

    flagPos = userIdLen + USER_ID_POS + GX_SIZE + SHA_DIGEST_LENGTH
    if struct.unpack(">I", data[flagPos + 1 : flagPos + 5])[0]:
        LOGGER.error("Second flag error!!!")
        return None

    sha1 = hashlib.sha1()
    sha1.update(dest)
    dest_hash = sha1.digest()
    LOGGER.debug("dest_hash: %s", dest_hash.hex())

    finalBuffer = (
        userId + user_id.encode("utf-8") + pGx + bytes.fromhex(PUBLIC_KEY) + secret
    )
    sha1 = hashlib.sha1()
    sha1.update(finalBuffer)
    SKPrime = sha1.digest()
    LOGGER.debug("SKPrime: %s", SKPrime.hex())
    sha1 = hashlib.sha1()
    sha1.update(SKPrime + b"\x00")
    SKPrimeHash = sha1.digest()
    LOGGER.debug("SKPrimeHash: %s", SKPrimeHash.hex())
    ctx = _apply_samy_go_key_transform(SKPrimeHash[:16])

    return {"ctx": ctx, "SKPrime": SKPrime}
```

---

### Summary of Changes
- Replaced `cryptography`'s `Cipher` with `pycryptodome`'s `AES`.
- Adjusted encryption and decryption logic to match `pycryptodome`'s API.
- Removed unnecessary finalization steps.