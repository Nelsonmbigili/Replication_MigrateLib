import typing
import unittest
from unittest.mock import Mock, patch

from whatsapp_api_client_python.API import GreenAPI
from whatsapp_api_client_python.response import Response

api = GreenAPI("", "")

path = "examples/data/rates.png"
import pytest


class MethodsTestCase(unittest.TestCase):
    @pytest.mark.asyncio
    @patch("whatsapp_api_client_python.API.Session.request")
    async def test_methods(self, mock_request):
        mock_request.return_value = Mock(
            status_code=200, text="""{"example": {"key": "value"}}"""
        )

        methods = [
            *self.account_methods,
            *self.device_methods,
            *self.group_methods,
            *self.log_methods,
            *self.queue_methods,
            *self.read_mark_methods,
            *self.receiving_methods,
            *self.sending_methods,
            *self.service_methods
        ]

        for response in methods:
            self.assertEqual(response.code, 200)
            self.assertEqual(response.data, {"example": {"key": "value"}})

        self.assertEqual(mock_request.call_count, len(methods))

    @property
    async def account_methods(self) -> typing.List[Response]:
        return [
            await api.account.getSettings(),
            await api.account.getWaSettings(),
            await api.account.setSettings({}),
            await api.account.getStateInstance(),
            await api.account.getStatusInstance(),
            await api.account.reboot(),
            await api.account.logout(),
            await api.account.qr(),
            await api.account.setProfilePicture(path),
            await api.account.getAuthorizationCode(0)
        ]

    @property
    async def device_methods(self) -> typing.List[Response]:
        return [await api.device.getDeviceInfo()]

    @property
    async def group_methods(self) -> typing.List[Response]:
        return [
            await api.groups.createGroup("", []),
            await api.groups.updateGroupName("", ""),
            await api.groups.getGroupData(""),
            await api.groups.addGroupParticipant("", ""),
            await api.groups.removeGroupParticipant("", ""),
            await api.groups.setGroupAdmin("", ""),
            await api.groups.removeAdmin("", ""),
            await api.groups.setGroupPicture("", path),
            await api.groups.leaveGroup("")
        ]

    @property
    async def log_methods(self) -> typing.List[Response]:
        return [
            await api.journals.getChatHistory(""),
            await api.journals.getMessage("", ""),
            await api.journals.lastIncomingMessages(),
            await api.journals.lastOutgoingMessages()
        ]

    @property
    async def queue_methods(self) -> typing.List[Response]:
        return [
            await api.queues.showMessagesQueue(),
            await api.queues.clearMessagesQueue()
        ]

    @property
    async def read_mark_methods(self) -> typing.List[Response]:
        return [await api.marking.readChat("")]

    @property
    async def receiving_methods(self) -> typing.List[Response]:
        return [
            await api.receiving.receiveNotification(),
            await api.receiving.deleteNotification(0),
            await api.receiving.downloadFile("", "")
        ]

    @property
    async def sending_methods(self) -> typing.List[Response]:
        return [
            await api.sending.sendMessage("", ""),
            await api.sending.sendButtons("", "", []),
            await api.sending.sendTemplateButtons("", "", []),
            await api.sending.sendListMessage("", "", "", []),
            await api.sending.sendFileByUpload("", path),
            await api.sending.sendFileByUrl("", "", ""),
            await api.sending.uploadFile(path),
            await api.sending.sendLocation("", 0.0, 0.0),
            await api.sending.sendContact("", {}),
            await api.sending.sendLink("", ""),
            await api.sending.forwardMessages("", "", []),
            await api.sending.sendPoll("", "", [])
        ]

    @property
    async def service_methods(self) -> typing.List[Response]:
        return [
            await api.serviceMethods.checkWhatsapp(0),
            await api.serviceMethods.getAvatar(""),
            await api.serviceMethods.getContacts(),
            await api.serviceMethods.getContactInfo(""),
            await api.serviceMethods.deleteMessage("", ""),
            await api.serviceMethods.archiveChat(""),
            await api.serviceMethods.unarchiveChat(""),
            await api.serviceMethods.setDisappearingChat("")
        ]


if __name__ == '__main__':
    unittest.main()
