import unittest
from unittest.mock import MagicMock, patch, Mock
import asyncio

import treq

from tinychat.llms.cohere import CohereClient
import pytest


class TestCohereClientStreaming(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    @patch("tinychat.llms.cohere.treq.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    async def test_perform_stream_request_success(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking the treq response
        mock_response = Mock()
        mock_response.code = 200
        mock_response.text.return_value = asyncio.Future()
        mock_response.text.return_value.set_result("Success")
        mock_post.return_value = asyncio.Future()
        mock_post.return_value.set_result(mock_response)

        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        response = await client.perform_stream_request("how are you?", chat_history)
        self.assertEqual(response.code, 200)

    @pytest.mark.asyncio
    @patch("tinychat.llms.cohere.treq.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    async def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking the treq response
        mock_response = Mock()
        mock_response.code = 400
        mock_response.text.return_value = asyncio.Future()
        mock_response.text.return_value.set_result("Error")
        mock_post.return_value = asyncio.Future()
        mock_post.return_value.set_result(mock_response)

        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        with self.assertRaises(ValueError) as context:
            await client.perform_stream_request("how are you?", chat_history)
        self.assertIn("Server responded with error: 400", str(context.exception))
