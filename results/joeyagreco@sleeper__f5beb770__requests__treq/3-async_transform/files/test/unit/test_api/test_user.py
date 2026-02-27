import unittest
from unittest.mock import patch

from sleeper.api import get_user
from test.unit.helper.helper_classes import MockResponse
import pytest


class TestUser(unittest.TestCase):
    @pytest.mark.asyncio
    @patch("requests.get")
    async def test_get_user(self, mock_requests_get):
        mock_dict = {"foo": "bar"}
        mock_response = MockResponse(mock_dict, 200)
        mock_requests_get.return_value = mock_response

        response = await get_user(identifier="foo")

        self.assertEqual(mock_dict, response)
        mock_requests_get.assert_called_once_with("https://api.sleeper.app/v1/user/foo")
