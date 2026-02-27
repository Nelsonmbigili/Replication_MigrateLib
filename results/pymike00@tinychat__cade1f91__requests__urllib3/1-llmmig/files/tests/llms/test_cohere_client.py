import unittest
from unittest.mock import MagicMock, patch, Mock

import urllib3

from tinychat.llms.cohere import CohereClient


class TestCohereClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.cohere.urllib3.PoolManager.request")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_request):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        mock_response = Mock(spec=urllib3.response.HTTPResponse)
        mock_response.status = 200
        mock_request.return_value = mock_response
        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        response = client.perform_stream_request("how are you?", chat_history)
        self.assertIsInstance(response, urllib3.response.HTTPResponse)
        self.assertEqual(response.status, 200)

    @patch("tinychat.llms.cohere.urllib3.PoolManager.request")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_request):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        mock_response = Mock(spec=urllib3.response.HTTPResponse)
        mock_response.status = 400
        mock_request.return_value = mock_response
        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        with self.assertRaises(ValueError) as context:
            client.perform_stream_request("how are you?", chat_history)
        self.assertIn("Server responded with error: 400", str(context.exception))
