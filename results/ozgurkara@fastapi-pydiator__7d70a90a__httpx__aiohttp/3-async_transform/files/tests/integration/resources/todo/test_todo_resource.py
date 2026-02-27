from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK
import aiohttp
import pytest


class TestTodo:

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_todo_all(self, test_app_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{test_app_url}/v1/todos") as response:
                assert response.status == HTTP_200_OK
                data = await response.json()
                items = data["items"]

                assert len(items) == 2
                assert items[0]["id"] == 1
                assert items[0]["title"] == "title 1"
                assert items[1]["id"] == 2
                assert items[1]["title"] == "title 2"

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_todo_by_id(self, test_app_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{test_app_url}/v1/todos/1") as response:
                assert response.status == HTTP_200_OK
                data = await response.json()
                assert data["id"] == 1
                assert data["title"] == "title 1"

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_add_todo(self, test_app_url):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{test_app_url}/v1/todos", json={
                "title": "title 3"
            }) as response:
                assert response.status == HTTP_200_OK
                data = await response.json()
                assert data["success"]

    @pytest.mark.asyncio
    async def test_add_todo_should_return_unprocessable_when_invalid_entity(self, test_app_url):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{test_app_url}/v1/todos", json=None) as response:
                assert response.status == HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_update_todo(self, test_app_url):
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{test_app_url}/v1/todos/1", json={
                "title": "title 1 updated"
            }) as response:
                assert response.status == HTTP_200_OK
                data = await response.json()
                assert data["success"]

    @pytest.mark.asyncio
    async def test_update_todo_should_return_unprocessable_when_invalid_entity(self, test_app_url):
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{test_app_url}/v1/todos/1", json={}) as response:
                assert response.status == HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_delete_todo(self, test_app_url):
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{test_app_url}/v1/todos/1") as response:
                assert response.status == HTTP_200_OK
                data = await response.json()
                assert data["success"]
