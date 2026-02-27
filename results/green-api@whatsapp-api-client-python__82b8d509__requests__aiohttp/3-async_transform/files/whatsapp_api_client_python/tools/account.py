from pathlib import Path
from typing import Dict, TYPE_CHECKING, Union

from ..response import Response

if TYPE_CHECKING:
    from ..API import GreenApi


class Account:
    def __init__(self, api: "GreenApi"):
        self.api = api

    async def getSettings(self) -> Response:
        """
        The method is aimed for getting the current account settings.

        https://green-api.com/en/docs/api/account/GetSettings/
        """

        return await self.api.request(
            "GET", (
                "{{host}}/waInstance{{idInstance}}/"
                "getSettings/{{apiTokenInstance}}"
            )
        )

    async def getWaSettings(self) -> Response:
        """
        The method is aimed to get information about the WhatsApp
        account.

        https://green-api.com/en/docs/api/account/GetWaSettings/
        """

        return await self.api.request(
            "GET", (
                "{{host}}/waInstance{{idInstance}}/"
                "getWaSettings/{{apiTokenInstance}}"
            )
        )

    async def setSettings(self, requestBody: Dict[str, Union[int, str]]) -> Response:
        """
        The method is aimed for setting account settings.

        https://green-api.com/en/docs/api/account/SetSettings/
        """

        return await self.api.request(
            "POST", (
                "{{host}}/waInstance{{idInstance}}/"
                "setSettings/{{apiTokenInstance}}"
            ), requestBody
        )

    async def getStateInstance(self) -> Response:
        """
        The method is aimed for getting the account state.

        https://green-api.com/en/docs/api/account/GetStateInstance/
        """

        return await self.api.request(
            "GET", (
                "{{host}}/waInstance{{idInstance}}/"
                "getStateInstance/{{apiTokenInstance}}"
            )
        )

    async def getStatusInstance(self) -> Response:
        """
        The method is aimed for getting the status of the account
        instance socket connection with WhatsApp.

        https://green-api.com/en/docs/api/account/GetStatusInstance/
        """

        return await self.api.request(
            "GET", (
                "{{host}}/waInstance{{idInstance}}/"
                "getStatusInstance/{{apiTokenInstance}}"
            )
        )

    async def reboot(self) -> Response:
        """
        The method is aimed for rebooting an account.

        https://green-api.com/en/docs/api/account/Reboot/
        """

        return await self.api.request(
            "GET", (
                "{{host}}/waInstance{{idInstance}}/reboot/{{apiTokenInstance}}"
            )
        )

    async def logout(self) -> Response:
        """
        The method is aimed for logging out an account.

        https://green-api.com/en/docs/api/account/Logout/
        """

        return await self.api.request(
            "GET", (
                "{{host}}/waInstance{{idInstance}}/logout/{{apiTokenInstance}}"
            )
        )

    async def qr(self) -> Response:
        """
        The method is aimed for getting QR code.

        https://green-api.com/en/docs/api/account/QR/
        """

        return await self.api.request(
            "GET", "{{host}}/waInstance{{idInstance}}/qr/{{apiTokenInstance}}"
        )

    async def setProfilePicture(self, path: str) -> Response:
        """
        The method is aimed for setting an account picture.

        https://green-api.com/en/docs/api/account/SetProfilePicture/
        """

        file_name = Path(path).name
        files = {"file": (file_name, open(path, "rb"), "image/jpeg")}

        return await self.api.request(
            "POST", (
                "{{host}}/waInstance{{idInstance}}/"
                "setProfilePicture/{{apiTokenInstance}}"
            ), files=files
        )

    async def getAuthorizationCode(self, phoneNumber: int) -> Response:
        """
        The method is designed to authorize an instance by phone number.

        https://green-api.com/en/docs/api/account/GetAuthorizationCode/
        """

        request_body = locals()
        request_body.pop("self")

        return await self.api.request(
            "POST", (
                "{{host}}/waInstance{{idInstance}}/"
                "getAuthorizationCode/{{apiTokenInstance}}"
            ), request_body
        )
