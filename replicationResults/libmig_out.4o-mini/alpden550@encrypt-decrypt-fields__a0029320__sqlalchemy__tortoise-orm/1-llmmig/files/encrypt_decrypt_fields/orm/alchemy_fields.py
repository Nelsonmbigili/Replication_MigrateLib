from tortoise import fields
from encrypt_decrypt_fields import Crypto


class EncryptedTortoiseBinaryField(fields.BinaryField):
    def __init__(self, key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key
        self.crypto = Crypto(key=self.key)

    def to_db_value(self, value, instance):
        if not value or isinstance(value, (bytes, memoryview)):
            return value

        return self.crypto.encrypt(str(value))

    def from_db_value(self, value, instance):
        if not value:
            return value

        return self.crypto.decrypt(value)
