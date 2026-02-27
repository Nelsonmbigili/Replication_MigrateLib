import resend
from resend.exceptions import NoContentError
from tests.conftest import ResendBaseTest
import pytest

# flake8: noqa


class TestResendContacts(ResendBaseTest):
    @pytest.mark.asyncio
    async def test_contacts_create(self) -> None:
        self.set_mock_json(
            {"object": "contact", "id": "479e3145-dd38-476b-932c-529ceb705947"}
        )

        params: resend.Contacts.CreateParams = {
            "audience_id": "48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
            "email": "steve.wozniak@gmail.com",
            "first_name": "Steve",
            "last_name": "Wozniak",
            "unsubscribed": True,
        }
        contact: resend.Contact = await resend.Contacts.create(params)
        assert contact["id"] == "479e3145-dd38-476b-932c-529ceb705947"

    @pytest.mark.asyncio
    async def test_should_create_contacts_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        params: resend.Contacts.CreateParams = {
            "audience_id": "48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
            "email": "steve.wozniak@gmail.com",
            "first_name": "Steve",
            "last_name": "Wozniak",
            "unsubscribed": True,
        }
        with self.assertRaises(NoContentError):
            _ = await resend.Contacts.create(params)

    @pytest.mark.asyncio
    async def test_contacts_update(self) -> None:
        self.set_mock_json(
            {
                "object": "contact",
                "id": "479e3145-dd38-476b-932c-529ceb705947",
            }
        )

        params: resend.Contacts.UpdateParams = {
            "audience_id": "48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
            "id": "479e3145-dd38-476b-932c-529ceb705947",
            "first_name": "Updated",
            "unsubscribed": True,
        }
        contact = await resend.Contacts.update(params)
        assert contact["id"] == "479e3145-dd38-476b-932c-529ceb705947"

    @pytest.mark.asyncio
    async def test_should_update_contacts_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        params: resend.Contacts.UpdateParams = {
            "audience_id": "48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
            "id": "479e3145-dd38-476b-932c-529ceb705947",
            "first_name": "Updated",
            "unsubscribed": True,
        }
        with self.assertRaises(NoContentError):
            _ = await resend.Contacts.update(params)

    @pytest.mark.asyncio
    async def test_contacts_get(self) -> None:
        self.set_mock_json(
            {
                "object": "contact",
                "id": "e169aa45-1ecf-4183-9955-b1499d5701d3",
                "email": "steve.wozniak@gmail.com",
                "first_name": "Steve",
                "last_name": "Wozniak",
                "created_at": "2023-10-06T23:47:56.678Z",
                "unsubscribed": False,
            }
        )

        contact: resend.Contact = await resend.Contacts.get(
            id="e169aa45-1ecf-4183-9955-b1499d5701d3",
            audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
        )
        assert contact["id"] == "e169aa45-1ecf-4183-9955-b1499d5701d3"
        assert contact["email"] == "steve.wozniak@gmail.com"
        assert contact["first_name"] == "Steve"
        assert contact["last_name"] == "Wozniak"
        assert contact["created_at"] == "2023-10-06T23:47:56.678Z"
        assert contact["unsubscribed"] is False

    @pytest.mark.asyncio
    async def test_should_get_contacts_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        with self.assertRaises(NoContentError):
            _ = await resend.Contacts.get(
                id="e169aa45-1ecf-4183-9955-b1499d5701d3",
                audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
            )

    @pytest.mark.asyncio
    async def test_contacts_remove_by_id(self) -> None:
        self.set_mock_json(
            {
                "object": "contact",
                "id": "520784e2-887d-4c25-b53c-4ad46ad38100",
                "deleted": True,
            }
        )

        rmed = await resend.Contacts.remove(
            audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
            id="78261eea-8f8b-4381-83c6-79fa7120f1cf",
        )
        assert rmed["id"] == "520784e2-887d-4c25-b53c-4ad46ad38100"
        assert rmed["deleted"] is True

    @pytest.mark.asyncio
    async def test_should_remove_contacts_by_id_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        with self.assertRaises(NoContentError):
            _ = await resend.Contacts.remove(
                audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
                id="78261eea-8f8b-4381-83c6-79fa7120f1cf",
            )

    @pytest.mark.asyncio
    async def test_contacts_remove_by_email(self) -> None:
        self.set_mock_json(
            {
                "object": "contact",
                "id": "520784e2-887d-4c25-b53c-4ad46ad38100",
                "deleted": True,
            }
        )

        rmed: resend.Contact = await resend.Contacts.remove(
            audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
            email="someemail@email.com",
        )
        assert rmed["id"] == "520784e2-887d-4c25-b53c-4ad46ad38100"
        assert rmed["deleted"] is True

    @pytest.mark.asyncio
    async def test_should_remove_contacts_by_email_raise_exception_when_no_content(
        self,
    ) -> None:
        self.set_mock_json(None)
        with self.assertRaises(NoContentError):
            _ = await resend.Contacts.remove(
                audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
                email="someemail@email.com",
            )

    @pytest.mark.asyncio
    async def test_contacts_remove_raises(self) -> None:
        resend.api_key = "re_123"

        with self.assertRaises(ValueError) as context:
            await resend.Contacts.remove(
                audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8",
            )

        self.assertEqual("id or email must be provided", str(context.exception))

    @pytest.mark.asyncio
    async def test_contacts_list(self) -> None:
        self.set_mock_json(
            {
                "object": "list",
                "data": [
                    {
                        "id": "e169aa45-1ecf-4183-9955-b1499d5701d3",
                        "email": "steve.wozniak@gmail.com",
                        "first_name": "Steve",
                        "last_name": "Wozniak",
                        "created_at": "2023-10-06T23:47:56.678Z",
                        "unsubscribed": False,
                    }
                ],
            }
        )

        contacts: resend.Contacts.ListResponse = await resend.Contacts.list(
            audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8"
        )
        assert contacts["data"][0]["id"] == "e169aa45-1ecf-4183-9955-b1499d5701d3"
        assert contacts["data"][0]["email"] == "steve.wozniak@gmail.com"
        assert contacts["data"][0]["first_name"] == "Steve"
        assert contacts["data"][0]["last_name"] == "Wozniak"
        assert contacts["data"][0]["created_at"] == "2023-10-06T23:47:56.678Z"
        assert contacts["data"][0]["unsubscribed"] is False

    @pytest.mark.asyncio
    async def test_should_list_contacts_raise_exception_when_no_content(self) -> None:
        self.set_mock_json(None)
        with self.assertRaises(NoContentError):
            _ = await resend.Contacts.list(audience_id="48c269ed-9873-4d60-bdd9-cd7e6fc0b9b8")
