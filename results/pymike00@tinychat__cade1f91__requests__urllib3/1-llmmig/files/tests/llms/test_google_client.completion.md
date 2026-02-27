### Explanation of Changes:
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Replaced `requests.post` with `urllib3.PoolManager.request`**:
   - `urllib3` does not have a `post` method like `requests`. Instead, we use the `request` method of `urllib3.PoolManager` and specify the HTTP method (`POST`) explicitly.
   - The `data` parameter in `requests.post` is replaced with the `body` parameter in `urllib3.PoolManager.request`.
   - The `headers` parameter remains the same.
2. **Replaced `Response` from `requests.models` with `urllib3.response.HTTPResponse`**:
   - The `Response` object from `requests` is replaced with `HTTPResponse` from `urllib3`.
   - The `status_code` attribute in `requests.Response` is replaced with the `status` attribute in `urllib3.response.HTTPResponse`.
3. **Mocking Changes**:
   - Updated the mock for `requests.post` to mock `urllib3.PoolManager.request` instead.
   - Adjusted the mocked response to match the behavior of `urllib3.response.HTTPResponse`.

### Modified Code:
```python
import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from urllib3.response import HTTPResponse

from tinychat.llms.google import GoogleAIClient


class TestGoogleAIClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.google.urllib3.PoolManager.request")
    @patch("tinychat.llms.google.SSEClient")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_sse_client, mock_request):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking SSEClient and the response
        mock_response = Mock(spec=HTTPResponse)
        mock_response.status = 200
        mock_request.return_value = mock_response

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

    @patch("tinychat.llms.google.urllib3.PoolManager.request")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_request):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Mocking the response with an error status code
        mock_response = Mock(spec=HTTPResponse)
        mock_response.status = 400
        mock_request.return_value = mock_response

        client = GoogleAIClient(temperature = 0.0)
        messages = [{"parts": [{"text": "content"}], "role": "user"}]

        with self.assertRaises(ValueError) as context:
            next(client.perform_stream_request(messages))  # type: ignore
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
```

### Key Points:
- The `requests.post` method was replaced with `urllib3.PoolManager.request` in the mocked calls.
- The `Response` object from `requests` was replaced with `HTTPResponse` from `urllib3`.
- The `status_code` attribute was replaced with the `status` attribute to check the HTTP response status.
- No other parts of the code were altered, ensuring compatibility with the rest of the application.