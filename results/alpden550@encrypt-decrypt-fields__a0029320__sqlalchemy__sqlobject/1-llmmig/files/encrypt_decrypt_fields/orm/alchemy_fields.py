from sqlobject import Col
from encrypt_decrypt_fields import Crypto


class EncryptedSQLObjectBinaryField(Col):
    def __init__(self, key: str, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.crypto = Crypto(key=self.key)

    def set(self, value):
        if not value or isinstance(value, (bytes, memoryview)):
            return value

        # Encrypt the value before storing it in the database
        return self.crypto.encrypt(str(value))

    def get(self, value):
        if not value or isinstance(value, (bytes, memoryview)):
            return value

        # Decrypt the value when retrieving it from the database
        return self.crypto.decrypt(value)
