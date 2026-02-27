from tortoise.fields import Field
from encrypt_decrypt_fields import Crypto


class EncryptedTortoiseBinaryField(Field):
    SQL_TYPE = "BLOB"  # Equivalent to BINARY in SQLAlchemy

    def __init__(self, key: str, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.crypto = Crypto(key=self.key)

    def to_db_value(self, value, instance):
        """
        Converts the Python value to a database-compatible value.
        """
        if not value or isinstance(value, (bytes, memoryview)):
            return value

        return self.crypto.encrypt(str(value))

    def to_python_value(self, value):
        """
        Converts the database value back to a Python object.
        """
        if not value or isinstance(value, (bytes, memoryview)):
            return value

        return self.crypto.decrypt(value)
