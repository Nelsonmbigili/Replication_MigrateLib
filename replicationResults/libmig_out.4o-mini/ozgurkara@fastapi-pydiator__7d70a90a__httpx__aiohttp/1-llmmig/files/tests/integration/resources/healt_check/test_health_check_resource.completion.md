### Explanation of Changes
To migrate the code from using the `httpx` library to the `aiohttp` library, the following changes were made:
1. The `test_app.get()` method from `httpx` was replaced with `await test_app.get()` to accommodate the asynchronous nature of `aiohttp`.
2. The `response` object handling remains similar, but since `aiohttp` is asynchronous, the test function was modified to be an `async` function.
3. The `assert` statements remain unchanged as they are not dependent on the HTTP client library.

### Modified Code
```python
from starlette.status import HTTP_200_OK


class TestTodo:

    async def test_get(self, test_app):
        response = await test_app.get("/health-check")

        assert response.status == HTTP_200_OK
        assert await response.read() == b"OK"
```