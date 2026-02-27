from starlette.status import HTTP_200_OK
import aiohttp
import pytest


class TestTodo:

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get(self, test_app):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{test_app}/health-check") as response:
                assert response.status == HTTP_200_OK
                assert await response.read() == b"OK"
