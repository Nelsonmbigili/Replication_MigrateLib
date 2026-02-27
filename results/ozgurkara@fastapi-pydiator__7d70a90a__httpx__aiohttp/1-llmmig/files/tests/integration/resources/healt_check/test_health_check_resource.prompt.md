The following Python code currently uses the library "httpx" version 0.26.0.
Migrate this code to use the library "aiohttp" version 3.11.18 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "httpx" to "aiohttp".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "httpx" and "aiohttp".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from starlette.status import HTTP_200_OK


class TestTodo:

    def test_get(self, test_app):
        response = test_app.get("/health-check")

        assert response.status_code == HTTP_200_OK
        assert response.content == b"OK"

```