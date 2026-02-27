### Explanation of Changes:
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. Replaced `requests.post` with `urllib3.PoolManager().request` for making HTTP POST requests.
2. Updated the mocking of `requests.post` to mock `urllib3.PoolManager.request` instead.
3. Adjusted the response handling to work with `urllib3`'s `HTTPResponse` object instead of `requests.models.Response`. Specifically:
   - `urllib3`'s `HTTPResponse` does not have a `status_code` attribute; instead, it uses `status`.
   - `urllib3`'s `HTTPResponse` does not have a `json()` method, so the response body is read using `.data` and then decoded and parsed with `json.loads()`.

### Modified Code:
```python
import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from tinychat.llms.anthropic import AnthropicAIClient


class TestAnthropicAIClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.anthropic.urllib3.PoolManager.request")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_request):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking the response
        mock_response = Mock()
        mock_response.status = 200
        mock_request.return_value = mock_response

        # Creating mock events
        mock_event1 = MagicMock()
        mock_event1.data = json.dumps(
            {"type": "content_block_delta", "delta": {"text": "part1"}}
        )
        mock_event2 = MagicMock()
        mock_event2.data = json.dumps(
            {"type": "content_block_delta", "delta": {"text": "part2"}}
        )
        mock_event_done = MagicMock()
        mock_event_done.data = json.dumps({"type": "done"})

        # Mocking SSEClient to return test events
        with patch("tinychat.llms.anthropic.SSEClient") as mock_sse_client:
            test_stream = iter([mock_event1, mock_event2, mock_event_done])
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

    @patch("tinychat.llms.anthropic.urllib3.PoolManager.request")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_request):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking the response with an error status code
        mock_response = Mock()
        mock_response.status = 400
        mock_request.return_value = mock_response

        client = AnthropicAIClient(model_name="test_model", temperature=0.0)
        messages = [{"role": "user", "content": "hello"}]

        with self.assertRaises(ValueError) as context:
            next(client.perform_stream_request(messages))
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
```

### Key Changes in Detail:
1. **Mocking `urllib3.PoolManager.request`**:
   - The `requests.post` method was replaced with `urllib3.PoolManager().request("POST", ...)`. To mock this, the `@patch` decorator was updated to patch `tinychat.llms.anthropic.urllib3.PoolManager.request`.

2. **Response Object Adjustments**:
   - `requests.models.Response` was replaced with `urllib3`'s `HTTPResponse`-like mock object.
   - The `status_code` attribute was replaced with `status` to match `urllib3`'s response object.
   - Since `urllib3` does not have a `json()` method, the response body would need to be read using `.data` and then parsed with `json.loads()` if necessary. However, this was not directly relevant in the provided code, as the response body was not used.

3. **No Changes to SSEClient**:
   - The `SSEClient` and its behavior were left unchanged, as it is unrelated to the migration from `requests` to `urllib3`.

This ensures the code now uses `urllib3` while maintaining the original functionality and structure.