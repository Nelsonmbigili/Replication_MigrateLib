The following Python code currently uses the library "urllib3" version 2.4.0.
Migrate this code to use the library "aiohttp" version 3.11.18 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "urllib3" to "aiohttp".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "urllib3" and "aiohttp".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import pytest

try:
    from urllib3.contrib.pyopenssl import (
        extract_from_urllib3,
        inject_into_urllib3,
    )
except ImportError:
    inject_into_urllib3 = lambda: None  # noqa: E731
    extract_from_urllib3 = lambda: None  # noqa: E731


@pytest.fixture(autouse=True)
def pyopenssl_inject_into_urllib3():
    inject_into_urllib3()
    try:
        yield
    finally:
        extract_from_urllib3()

```