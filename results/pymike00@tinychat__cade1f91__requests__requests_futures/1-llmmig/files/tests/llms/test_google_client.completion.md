### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class provided by `requests_futures`.
2. **Session Initialization**: Updated the `requests.post` calls to use an instance of `FuturesSession` for asynchronous HTTP requests.
3. **Mocking Changes**: Updated the `@patch` decorators to mock `requests_futures.sessions.FuturesSession.post` instead of `requests.post`.
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual `Response` object in the test cases.

### Modified Code
```python
import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from requests.models import Response

from tinychat.llms.google import GoogleAIClient


class TestGoogleAIClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.google.requests_futures.sessions.FuturesSession.post")
    @patch("tinychat.llms.google.SSEClient")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_sse_client, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking SSEClient and the response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_post.return_value.result.return_value = mock_response  # Use .result() for FuturesSession

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

        client = GoogleAIClient(temperature = 0.0)
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

    @patch("tinychat.llms.google.requests_futures.sessions.FuturesSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking the response with an error status code
        mock_response = Mock(spec=Response)
        mock_response.status_code = 400
        mock_post.return_value.result.return_value = mock_response  # Use .result() for FuturesSession

        client = GoogleAIClient(temperature = 0.0)
        messages = [{"parts": [{"text": "content"}], "role": "user"}]

        with self.assertRaises(ValueError) as context:
            next(client.perform_stream_request(messages))  # type: ignore
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
```

### Key Points
- The `mock_post.return_value.result.return_value` is used to simulate the behavior of `FuturesSession.post`, which returns a `Future` object. The `.result()` method is called to retrieve the actual `Response` object.
- The `@patch` decorators now target `requests_futures.sessions.FuturesSession.post` instead of `requests.post`.
- No other parts of the code were modified, ensuring the migration is focused solely on replacing `requests` with `requests_futures`.