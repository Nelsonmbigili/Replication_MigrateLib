import json
import unittest
from unittest.mock import MagicMock, Mock, patch
import io

from tinychat.llms.google import GoogleAIClient


class TestGoogleAIClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.google.pycurl.Curl")
    @patch("tinychat.llms.google.SSEClient")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_sse_client, mock_curl):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking SSEClient and the response
        mock_curl_instance = mock_curl.return_value
        response_data = (
            '{"candidates": [{"content": {"parts": [{"text": "part1"}]}}]}\n'
            '{"candidates": [{"content": {"parts": [{"text": "part2"}]}}]}\n'
            "[DONE]"
        )
        response_buffer = io.BytesIO(response_data.encode("utf-8"))
        mock_curl_instance.perform.side_effect = lambda: response_buffer.seek(0)
        mock_curl_instance.getinfo.return_value = 200  # Simulate HTTP 200 status code

        # Creating mock events
        mock_event1 = MagicMock()
        mock_event1.data = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "part1"}]}}]}
        )
        mock_event2 = MagicMock()
        mock_event2.data = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "part2"}]}}]}
        )
        mock_event_done = MagicMock()
        mock_event_done.data = "[DONE]"

        # Setting up a test stream
        test_stream = [mock_event1, mock_event2, mock_event_done]
        mock_sse_client.return_value.events = MagicMock(return_value=iter(test_stream))

        client = GoogleAIClient(temperature=0.0)
        messages = [{"parts": [{"text": "content"}], "role": "user"}]
        stream = client.perform_stream_request(messages)

        # Extracting and verifying the stream response
        responses = []
        for event in stream.events():
            if event.data != "[DONE]":
                event_data = json.loads(event.data)
                response_piece = event_data["candidates"][0]["content"]["parts"][0][
                    "text"
                ]
                responses.append(response_piece)

        self.assertEqual(responses, ["part1", "part2"])

    @patch("tinychat.llms.google.pycurl.Curl")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_curl):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking the response with an error status code
        mock_curl_instance = mock_curl.return_value
        mock_curl_instance.getinfo.return_value = 400  # Simulate HTTP 400 status code
        response_buffer = io.BytesIO(b"")
        mock_curl_instance.perform.side_effect = lambda: response_buffer.seek(0)

        client = GoogleAIClient(temperature=0.0)
        messages = [{"parts": [{"text": "content"}], "role": "user"}]

        with self.assertRaises(ValueError) as context:
            next(client.perform_stream_request(messages))  # type: ignore
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
