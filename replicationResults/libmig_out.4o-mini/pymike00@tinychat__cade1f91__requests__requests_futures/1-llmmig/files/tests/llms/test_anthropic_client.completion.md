### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The import statement for `requests` was replaced with `requests_futures.sessions`.
2. **Session Creation**: Instead of using `requests.post`, we now use `FuturesSession` from `requests_futures.sessions` to make asynchronous requests.
3. **Handling Responses**: The response handling remains largely the same, but we need to ensure that we wait for the future to complete before accessing the response.

### Modified Code
Here is the modified code after migrating to `requests_futures`:

```python
import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from requests_futures.sessions import FuturesSession

from tinychat.llms.anthropic import AnthropicAIClient


class TestAnthropicAIClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.anthropic.FuturesSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking the response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_post.return_value = mock_response

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

    @patch("tinychat.llms.anthropic.FuturesSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking the response with an error status code
        mock_response = Mock(spec=Response)
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        client = AnthropicAIClient(model_name="test_model", temperature=0.0)
        messages = [{"role": "user", "content": "hello"}]

        with self.assertRaises(ValueError) as context:
            next(client.perform_stream_request(messages))
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
```

In this modified code, the `requests.post` calls have been replaced with `FuturesSession.post`, allowing for asynchronous handling of requests while maintaining the original structure and logic of the code.