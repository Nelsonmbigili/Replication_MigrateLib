import resend
from resend.exceptions import NoContentError
from tests.conftest import ResendBaseTest
import pytest

# flake8: noqa


class TestResendAudiences(ResendBaseTest):
    @pytest.mark.asyncio
    async def test_audiences_create(self) -> None:
        self.set_mock_json(
            {
                "object": "audience",
                "id": "78261eea-8f8b-4381-83c6-79fa7120f1cf",
                "name": "Registered Users",
            }
        )

        params: resend.Audiences.CreateParams = {
            "name": "Python SDK Audience",
        }
        audience = await resend.Audiences.create(params)
        assert audience["id"] == "78261eea-8f8b-4381-83c6-79fa7120f1cf"
        assert audience["name"] == "Registered Users"

    @pytest.mark.asyncio
    async def test_should_create_audiences_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        params: resend.Audiences.CreateParams = {
            "name": "Python SDK Audience",
        }
        with self.assertRaises(NoContentError):
            _ = await resend.Audiences.create(params)

    @pytest.mark.asyncio
    async def test_audiences_get(self) -> None:
        self.set_mock_json(
            {
                "object": "audience",
                "id": "78261eea-8f8b-4381-83c6-79fa7120f1cf",
                "name": "Registered Users",
                "created_at": "2023-10-06T22:59:55.977Z",
            }
        )

        audience = await resend.Audiences.get(id="78261eea-8f8b-4381-83c6-79fa7120f1cf")
        assert audience["id"] == "78261eea-8f8b-4381-83c6-79fa7120f1cf"
        assert audience["name"] == "Registered Users"
        assert audience["created_at"] == "2023-10-06T22:59:55.977Z"

    @pytest.mark.asyncio
    async def test_should_get_audiences_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        with self.assertRaises(NoContentError):
            _ = await resend.Audiences.get(id="78261eea-8f8b-4381-83c6-79fa7120f1cf")

    @pytest.mark.asyncio
    async def test_audiences_remove(self) -> None:
        self.set_mock_json(
            {
                "object": "audience",
                "id": "78261eea-8f8b-4381-83c6-79fa7120f1cf",
                "deleted": True,
            }
        )

        rmed = await resend.Audiences.remove("78261eea-8f8b-4381-83c6-79fa7120f1cf")
        assert rmed["id"] == "78261eea-8f8b-4381-83c6-79fa7120f1cf"
        assert rmed["deleted"] is True

    @pytest.mark.asyncio
    async def test_should_remove_audiences_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        with self.assertRaises(NoContentError):
            _ = await resend.Audiences.remove(id="78261eea-8f8b-4381-83c6-79fa7120f1cf")

    @pytest.mark.asyncio
    async def test_audiences_list(self) -> None:
        self.set_mock_json(
            {
                "object": "list",
                "data": [
                    {
                        "id": "78261eea-8f8b-4381-83c6-79fa7120f1cf",
                        "name": "Registered Users",
                        "created_at": "2023-10-06T22:59:55.977Z",
                    }
                ],
            }
        )

        audiences: resend.Audiences.ListResponse = await resend.Audiences.list()
        assert audiences["data"][0]["id"] == "78261eea-8f8b-4381-83c6-79fa7120f1cf"
        assert audiences["data"][0]["name"] == "Registered Users"

    @pytest.mark.asyncio
    async def test_should_list_audiences_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        with self.assertRaises(NoContentError):
            _ = await resend.Audiences.list()
