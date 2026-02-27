The following Python code currently uses the library "sqlalchemy" version 1.4.54.
Migrate this code to use the library "tortoise-orm" version 0.24.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "sqlalchemy" to "tortoise-orm".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "sqlalchemy" and "tortoise-orm".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from sqlalchemy.types import TypeDecorator, BINARY

from encrypt_decrypt_fields import Crypto


class EncryptedAlchemyBinaryField(TypeDecorator):
    impl = BINARY

    def __init__(self, key: str, *arg, **kwargs):
        TypeDecorator.__init__(self, *arg, **kwargs)
        self.key = key
        self.crypto = Crypto(key=self.key)

    def process_bind_param(self, value, dialect):
        if not value or isinstance(value, (bytes, memoryview)):
            return value

        return self.crypto.encrypt(str(value))

```