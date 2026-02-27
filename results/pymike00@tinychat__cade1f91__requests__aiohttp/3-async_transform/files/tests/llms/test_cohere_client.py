import unittest
from unittest.mock import AsyncMock, MagicMock, patch, Mock

import aiohttp

from tinychat.llms.cohere import CohereClient
import pytest


class TestCohereClientStreaming(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    @patch("tinychat.llms.cohere.aiohttp.ClientSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    async def test_perform_stream_request_success(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking aiohttp response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_post.return_value = mock_response

        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        response = await client.perform_stream_request("how are you?", chat_history)
        self.assertIsInstance(response, aiohttp.ClientResponse)
        self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    @patch("tinychat.llms.cohere.aiohttp.ClientSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    async def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking aiohttp response
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_post.return_value = mock_response

        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        with self.assertRaises(ValueError) as context:
            await client.perform_stream_request("how are you?", chat_history)
        self.assertIn("Server responded with error: 400", str(context.exception))
