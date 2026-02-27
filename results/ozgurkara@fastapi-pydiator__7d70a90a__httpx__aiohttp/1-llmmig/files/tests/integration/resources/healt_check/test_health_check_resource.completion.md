### Explanation of Changes:
To migrate from `httpx` to `aiohttp`, the following changes were made:
1. Replaced the `httpx`-specific `test_app.get` method with `aiohttp`'s `ClientSession` and its `get` method.
2. Used `async` and `await` since `aiohttp` is asynchronous.
3. Updated the test method to be asynchronous (`async def`) to accommodate `aiohttp`'s asynchronous nature.
4. Used `response.status` instead of `response.status_code` to check the HTTP status code, as per `aiohttp`'s API.
5. Used `await response.read()` to access the response content, as `aiohttp` requires explicit reading of the response body.

### Modified Code:
```python
from starlette.status import HTTP_200_OK
import aiohttp
import pytest


class TestTodo:

    @pytest.mark.asyncio
    async def test_get(self, test_app):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{test_app}/health-check") as response:
                assert response.status == HTTP_200_OK
                assert await response.read() == b"OK"
```