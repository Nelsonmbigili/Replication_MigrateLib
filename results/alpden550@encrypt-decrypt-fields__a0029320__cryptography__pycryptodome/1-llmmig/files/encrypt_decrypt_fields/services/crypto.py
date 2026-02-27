import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes


class Crypto:
    def __init__(self, key: str):
        self.key = key

    def get_key(self) -> bytes:
        # Derive a 32-byte key using SHA256
        digest = SHA256.new()
        digest.update(self.key.encode())
        return digest.digest()

    def encrypt(self, password: str) -> bytes:
        # Generate a random nonce
        nonce = get_random_bytes(12)
        key = self.get_key()
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(password.encode())

        # Combine nonce, tag, and ciphertext, then encode in base64
        return base64.urlsafe_b64encode(nonce + tag + ciphertext)

    def decrypt_token(self, token: bytes | None) -> str | None:
        if not token:
            return None

        # Decode the base64 token
        decoded_data = base64.urlsafe_b64decode(token)

        # Extract nonce, tag, and ciphertext
        nonce = decoded_data[:12]
        tag = decoded_data[12:28]
        ciphertext = decoded_data[28:]

        key = self.get_key()
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        # Decrypt and verify the ciphertext
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
