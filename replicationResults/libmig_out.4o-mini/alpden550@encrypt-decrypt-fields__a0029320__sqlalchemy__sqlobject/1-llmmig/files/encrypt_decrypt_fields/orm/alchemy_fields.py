from sqlobject import StringCol
from encrypt_decrypt_fields import Crypto

class EncryptedSQLObjectBinaryField(StringCol):
    def __init__(self, key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key
        self.crypto = Crypto(key=self.key)

    def setValue(self, value):
        if not value or isinstance(value, (bytes, memoryview)):
            return value

        return self.crypto.encrypt(str(value))
