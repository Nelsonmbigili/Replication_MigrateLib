import unittest
from unittest.mock import MagicMock, patch, Mock
from requests_futures.sessions import FuturesSession

from tinychat.llms.cohere import CohereClient


class TestCohereClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.cohere.FuturesSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking a Future object with a Response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        future_mock = Mock()
        future_mock.result.return_value = mock_response
        mock_post.return_value = future_mock

        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        response = client.perform_stream_request("how are you?", chat_history)
        self.assertIsInstance(response, requests.Response)
        self.assertEqual(response.status_code, 200)

    @patch("tinychat.llms.cohere.FuturesSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking a Future object with a Response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 400
        future_mock = Mock()
        future_mock.result.return_value = mock_response
        mock_post.return_value = future_mock

        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        with self.assertRaises(ValueError) as context:
            client.perform_stream_request("how are you?", chat_history)
        self.assertIn("Server responded with error: 400", str(context.exception))
