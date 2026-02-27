from typing import TYPE_CHECKING

from ..response import Response

if TYPE_CHECKING:
    from ..API import GreenApi


class Queues:
    def __init__(self, api: "GreenApi"):
        self.api = api

    async def showMessagesQueue(self) -> Response:
        """
        The method is aimed for getting a list of messages in the queue
        to be sent.

        https://green-api.com/en/docs/api/queues/ShowMessagesQueue/
        """

        return await self.api.request(
            "GET", (
                "{{host}}/waInstance{{idInstance}}/"
                "showMessagesQueue/{{apiTokenInstance}}"
            )
        )

    async def clearMessagesQueue(self) -> Response:
        """
        The method is aimed for clearing the queue of messages to be
        sent.

        https://green-api.com/en/docs/api/queues/ClearMessagesQueue/
        """

        return await self.api.request(
            "GET", (
                "{{host}}/waInstance{{idInstance}}/"
                "clearMessagesQueue/{{apiTokenInstance}}"
            )
        )
