import unittest
from unittest.mock import MagicMock, patch, Mock
import aiohttp
import asyncio

from tinychat.llms.cohere import CohereClient


class TestCohereClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.cohere.aiohttp.ClientSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(client.perform_stream_request("how are you?", chat_history))
        self.assertIsInstance(response, aiohttp.ClientResponse)
        self.assertEqual(response.status, 200)

    @patch("tinychat.llms.cohere.aiohttp.ClientSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        mock_response = Mock()
        mock_response.status = 400
        mock_response.__aenter__.return_value = mock_response
        mock_post.return_value = mock_response
        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        loop = asyncio.get_event_loop()
        with self.assertRaises(ValueError) as context:
            loop.run_until_complete(client.perform_stream_request("how are you?", chat_history))
        self.assertIn("Server responded with error: 400", str(context.exception))
