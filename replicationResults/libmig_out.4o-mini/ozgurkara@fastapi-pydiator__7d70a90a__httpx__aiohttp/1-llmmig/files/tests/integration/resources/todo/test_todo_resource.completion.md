### Explanation of Changes
To migrate the code from using the `httpx` library to the `aiohttp` library, the following changes were made:

1. **Importing aiohttp**: The `httpx` library is replaced with `aiohttp` for making HTTP requests.
2. **Using `aiohttp.ClientSession`**: Instead of calling `test_app.get`, `test_app.post`, etc., we create an instance of `aiohttp.ClientSession` and use it to make asynchronous requests.
3. **Awaiting Responses**: Since `aiohttp` is asynchronous, we need to use `await` when making requests and when calling methods like `.json()`.
4. **Handling JSON Responses**: The way to handle JSON responses is slightly different in `aiohttp`, requiring the use of `await response.json()`.

The overall structure of the tests remains the same, but the method of making requests and handling responses has been updated to fit the `aiohttp` library's API.

### Modified Code
```python
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK
import aiohttp
import asyncio

class TestTodo:

    async def fetch(self, session, method, url, json=None):
        async with session.request(method, url, json=json) as response:
            return await response.json(), response.status

    async def test_get_todo_all(self, test_app):
        async with aiohttp.ClientSession() as session:
            items, status_code = await self.fetch(session, 'GET', "/v1/todos")
        
        assert status_code == HTTP_200_OK
        assert len(items["items"]) == 2
        assert items["items"][0]["id"] == 1
        assert items["items"][0]["title"] == "title 1"
        assert items["items"][1]["id"] == 2
        assert items["items"][1]["title"] == "title 2"

    async def test_get_todo_by_id(self, test_app):
        async with aiohttp.ClientSession() as session:
            item, status_code = await self.fetch(session, 'GET', "/v1/todos/1")
        
        assert status_code == HTTP_200_OK
        assert item["id"] == 1
        assert item["title"] == "title 1"

    async def test_add_todo(self, test_app):
        async with aiohttp.ClientSession() as session:
            response, status_code = await self.fetch(session, 'POST', "/v1/todos", json={
                "title": "title 3"
            })
        
        assert status_code == HTTP_200_OK
        assert response["success"]

    async def test_add_todo_should_return_unprocessable_when_invalid_entity(self, test_app):
        async with aiohttp.ClientSession() as session:
            response, status_code = await self.fetch(session, 'POST', "/v1/todos", json=None)
        
        assert status_code == HTTP_422_UNPROCESSABLE_ENTITY

    async def test_update_todo(self, test_app):
        async with aiohttp.ClientSession() as session:
            response, status_code = await self.fetch(session, 'PUT', "/v1/todos/1", json={
                "title": "title 1 updated"
            })
        
        assert status_code == HTTP_200_OK
        assert response["success"]

    async def test_update_todo_should_return_unprocessable_when_invalid_entity(self, test_app):
        async with aiohttp.ClientSession() as session:
            response, status_code = await self.fetch(session, 'PUT', "/v1/todos/1", json={})
        
        assert status_code == HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete_todo(self, test_app):
        async with aiohttp.ClientSession() as session:
            response, status_code = await self.fetch(session, 'DELETE', "/v1/todos/1")
        
        assert status_code == HTTP_200_OK
        assert response["success"]
```

In this modified code, all HTTP requests are now made using `aiohttp.ClientSession`, and the responses are awaited properly to handle the asynchronous nature of the library.