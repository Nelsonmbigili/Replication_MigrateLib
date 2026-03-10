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
