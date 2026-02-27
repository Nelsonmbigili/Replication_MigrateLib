import unittest

from sleeper.api import get_user
from test.integration.test_api.constants import (
    USER_B_USER,
    USER_B_USER_ID,
    USER_B_USERNAME,
)
import pytest


class TestUser(unittest.TestCase):
    @pytest.mark.asyncio
    async def test_get_user_with_user_id_as_identifier(self):
        response = await get_user(identifier=USER_B_USER_ID)
        self.assertEqual(response, USER_B_USER)

    @pytest.mark.asyncio
    async def test_get_user_with_username_as_identifier(self):
        response = await get_user(identifier=USER_B_USERNAME)
        self.assertEqual(response, USER_B_USER)
