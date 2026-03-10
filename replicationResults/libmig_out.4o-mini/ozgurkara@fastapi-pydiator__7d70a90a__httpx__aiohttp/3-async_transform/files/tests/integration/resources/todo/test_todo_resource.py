from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK
import aiohttp
import asyncio
import pytest

class TestTodo:

    async def fetch(self, session, method, url, json=None):
        async with session.request(method, url, json=json) as response:
            return await response.json(), response.status

    @pytest.mark.asyncio
    async def test_get_todo_all(self, test_app):
        async with aiohttp.ClientSession() as session:
            items, status_code = await self.fetch(session, 'GET', "/v1/todos")
        
        assert status_code == HTTP_200_OK
        assert len(items["items"]) == 2
        assert items["items"][0]["id"] == 1
        assert items["items"][0]["title"] == "title 1"
        assert items["items"][1]["id"] == 2
        assert items["items"][1]["title"] == "title 2"

    @pytest.mark.asyncio
    async def test_get_todo_by_id(self, test_app):
        async with aiohttp.ClientSession() as session:
            item, status_code = await self.fetch(session, 'GET', "/v1/todos/1")
        
        assert status_code == HTTP_200_OK
        assert item["id"] == 1
        assert item["title"] == "title 1"

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_delete_todo(self, test_app):
        async with aiohttp.ClientSession() as session:
            response, status_code = await self.fetch(session, 'DELETE', "/v1/todos/1")
        
        assert status_code == HTTP_200_OK
        assert response["success"]
