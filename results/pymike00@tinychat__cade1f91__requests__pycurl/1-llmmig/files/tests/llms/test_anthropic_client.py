import json
import unittest
from unittest.mock import MagicMock, Mock, patch
import io

import pycurl

from tinychat.llms.anthropic import AnthropicAIClient


class TestAnthropicAIClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.anthropic.pycurl.Curl")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_curl):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking the pycurl.Curl object
        mock_curl_instance = Mock()
        mock_curl.return_value = mock_curl_instance

        # Mocking the response data
        response_data = json.dumps(
            {"type": "content_block_delta", "delta": {"text": "part1"}}
        ) + "\n" + json.dumps(
            {"type": "content_block_delta", "delta": {"text": "part2"}}
        ) + "\n" + json.dumps({"type": "done"})

        # Simulating the response buffer
        response_buffer = io.BytesIO(response_data.encode("utf-8"))
        mock_curl_instance.perform.side_effect = lambda: response_buffer.seek(0)
        mock_curl_instance.getinfo.return_value = 200  # Mocking HTTP status code

        # Mocking SSEClient to return test events
        with patch("tinychat.llms.anthropic.SSEClient") as mock_sse_client:
            test_stream = iter(
                [
                    MagicMock(data=json.dumps({"type": "content_block_delta", "delta": {"text": "part1"}})),
                    MagicMock(data=json.dumps({"type": "content_block_delta", "delta": {"text": "part2"}})),
                    MagicMock(data=json.dumps({"type": "done"})),
                ]
            )
            mock_sse_client.return_value.events = MagicMock(return_value=test_stream)

            client = AnthropicAIClient(model_name="test_model", temperature=0.0)
            messages = [{"role": "user", "content": "hello"}]
            stream = client.perform_stream_request(messages)

            # Extracting and verifying the stream response
            responses = []
            for event in stream.events():
                event_data = json.loads(event.data)
                if event_data.get("type") == "content_block_delta":
                    responses.append(event_data["delta"]["text"])

            self.assertEqual(responses, ["part1", "part2"])

    @patch("tinychat.llms.anthropic.pycurl.Curl")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_curl):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking the pycurl.Curl object
        mock_curl_instance = Mock()
        mock_curl.return_value = mock_curl_instance

        # Simulating an error response
        response_data = "Error occurred"
        response_buffer = io.BytesIO(response_data.encode("utf-8"))
        mock_curl_instance.perform.side_effect = lambda: response_buffer.seek(0)
        mock_curl_instance.getinfo.return_value = 400  # Mocking HTTP status code

        client = AnthropicAIClient(model_name="test_model", temperature=0.0)
        messages = [{"role": "user", "content": "hello"}]

        with self.assertRaises(ValueError) as context:
            next(client.perform_stream_request(messages))
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
