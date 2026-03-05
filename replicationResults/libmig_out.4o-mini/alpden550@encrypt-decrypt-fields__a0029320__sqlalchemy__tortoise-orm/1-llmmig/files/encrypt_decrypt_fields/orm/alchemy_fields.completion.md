### Explanation of Changes
To migrate the code from using SQLAlchemy to Tortoise-ORM, the following changes were made:

1. **Import Changes**: The `TypeDecorator` and `BINARY` types from SQLAlchemy were replaced with Tortoise-ORM's equivalent. Tortoise-ORM does not have a direct equivalent for `TypeDecorator`, so we will create a custom field type.
2. **Field Definition**: Tortoise-ORM uses a different way to define custom fields. Instead of subclassing `TypeDecorator`, we will create a custom field class that inherits from `Field`.
3. **Method Changes**: The method for processing the binding of parameters is adapted to fit Tortoise-ORM's structure.

### Modified Code
```python
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
``` 

In this modified code, we have created a new class `EncryptedTortoiseBinaryField` that extends `fields.BinaryField` from Tortoise-ORM. The `process_bind_param` method from SQLAlchemy is replaced with `to_db_value` and `from_db_value` methods to handle the conversion of values to and from the database.