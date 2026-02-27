import unittest
from unittest.mock import MagicMock, patch, Mock
from io import BytesIO

import pycurl

from tinychat.llms.cohere import CohereClient


class TestCohereClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.cohere.pycurl.Curl")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_curl):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking pycurl.Curl behavior
        mock_curl_instance = Mock()
        mock_curl.return_value = mock_curl_instance

        # Simulate a successful response
        response_body = b'{"status": "success"}'
        response_buffer = BytesIO(response_body)
        mock_curl_instance.perform.side_effect = lambda: response_buffer.seek(0)
        mock_curl_instance.getinfo.return_value = 200  # Simulate HTTP 200 status code

        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        response = client.perform_stream_request("how are you?", chat_history)

        # Assertions
        self.assertIsInstance(response, BytesIO)
        self.assertEqual(mock_curl_instance.getinfo(pycurl.RESPONSE_CODE), 200)

    @patch("tinychat.llms.cohere.pycurl.Curl")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_curl):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking pycurl.Curl behavior
        mock_curl_instance = Mock()
        mock_curl.return_value = mock_curl_instance

        # Simulate a failed response
        response_body = b'{"status": "error"}'
        response_buffer = BytesIO(response_body)
        mock_curl_instance.perform.side_effect = lambda: response_buffer.seek(0)
        mock_curl_instance.getinfo.return_value = 400  # Simulate HTTP 400 status code

        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        with self.assertRaises(ValueError) as context:
            client.perform_stream_request("how are you?", chat_history)

        # Assertions
        self.assertIn("Server responded with error: 400", str(context.exception))
