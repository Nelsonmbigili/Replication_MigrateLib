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
