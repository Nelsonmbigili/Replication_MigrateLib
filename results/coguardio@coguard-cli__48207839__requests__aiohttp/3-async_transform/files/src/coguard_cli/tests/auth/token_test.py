"""
Tests for the token class.
"""

import unittest
import unittest.mock
import aiohttp
from coguard_cli.auth.token import Token
from coguard_cli.auth.auth_config import CoGuardCliConfig
from coguard_cli.auth.util import DealEnum
import pytest

class TestTokenClass(unittest.IsolatedAsyncioTestCase):
    """
    The class for testing the token class.
    """

    @pytest.mark.asyncio
    async def test_get_public_key_status_not_200(self):
        """
        Tests the public key extraction of the authentication server.
        """
        async def mock_get(*args, **kwargs):
            class MockResponse:
                @property
                def status(self):
                    return 420
            return MockResponse()

        mock_config_object = unittest.mock.Mock(
            get_auth_url=lambda: "https://portal.coguard.io"
        )
        token = Token("foo", mock_config_object)
        with unittest.mock.patch('aiohttp.ClientSession.get', new=mock_get):
            result = await token.get_public_key()
            self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_get_public_key_status_200_no_public_key(self):
        """
        Tests the public key extraction of the authentication server.
        """
        async def mock_get(*args, **kwargs):
            class MockResponse:
                @property
                def status(self):
                    return 200

                async def json(self):
                    return {}
            return MockResponse()

        mock_config_object = unittest.mock.Mock(
            get_auth_url=lambda: "https://portal.coguard.io/auth"
        )
        token = Token("foo", mock_config_object)
        with unittest.mock.patch('aiohttp.ClientSession.get', new=mock_get):
            result = await token.get_public_key()
            self.assertIsNone(result)

    @pytest.mark.asyncio
    async def test_get_public_key_status_200_public_key(self):
        """
        Tests the public key extraction of the authentication server.
        """
        async def mock_get(*args, **kwargs):
            class MockResponse:
                @property
                def status(self):
                    return 200

                async def json(self):
                    return {"public_key": "123456"}
            return MockResponse()

        mock_config_object = unittest.mock.Mock(
            get_auth_url=lambda: "https://portal.coguard.io/auth"
        )
        token = Token("foo", mock_config_object)
        with unittest.mock.patch('aiohttp.ClientSession.get', new=mock_get):
            result = await token.get_public_key()
            self.assertEqual(result, "123456")

    @pytest.mark.asyncio
    async def test_authenticate_to_server_empty_config_object(self):
        """
        Tests that the authentication returns None if the configuration object is None
        """
        token = Token("foo", None)
        self.assertIsNone(await token.authenticate_to_server())

    @pytest.mark.asyncio
    async def test_authenticate_to_server_non_empty_config_object_404(self):
        """
        Tests that the authentication returns None if the status code
        is not 200.
        """
        config_obj = CoGuardCliConfig("foo", "bar")

        async def mock_post(*args, **kwargs):
            class MockResponse:
                @property
                def status(self):
                    return 404
            return MockResponse()

        with unittest.mock.patch('aiohttp.ClientSession.post', new=mock_post):
            token = Token("foo", config_obj)
            self.assertIsNone(await token.authenticate_to_server())

    @pytest.mark.asyncio
    async def test_authenticate_to_server_non_empty_config_object_success(self):
        """
        Tests that the authentication returns None if the status code
        is not 200.
        """
        config_obj = CoGuardCliConfig("foo", "bar")

        async def mock_post(*args, **kwargs):
            class MockResponse:
                @property
                def status(self):
                    return 200

                async def json(self):
                    return {"access_token": "foo"}
            return MockResponse()

        with unittest.mock.patch('aiohttp.ClientSession.post', new=mock_post):
            token = Token("foo", config_obj)
            result = await token.authenticate_to_server()
            self.assertIsNotNone(result)
            self.assertEqual(result, "foo")
