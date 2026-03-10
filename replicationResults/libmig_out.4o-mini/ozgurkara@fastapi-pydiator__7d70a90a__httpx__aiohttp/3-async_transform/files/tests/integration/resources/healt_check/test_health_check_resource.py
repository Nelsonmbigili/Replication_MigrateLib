from starlette.status import HTTP_200_OK
import pytest


class TestTodo:

    @pytest.mark.asyncio
    async def test_get(self, test_app):
        response = await test_app.get("/health-check")

        assert response.status == HTTP_200_OK
        assert await response.read() == b"OK"
