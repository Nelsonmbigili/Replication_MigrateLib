The following Python code currently uses the library "requests" version 2.31.0.
Migrate this code to use the library "aiohttp" version 3.11.16 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "aiohttp".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "aiohttp".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import json
import unittest
from unittest.mock import MagicMock, Mock, patch

from requests.models import Response

from tinychat.llms.mistral import MistralClient


class TestMistralClientStreaming(unittest.TestCase):
    @patch("tinychat.llms.mistral.requests.post")
    @patch("tinychat.llms.mistral.SSEClient")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(self, mock_api_key, mock_sse_client, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Setup: Mocking SSEClient and the response
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Creating mock events
        mock_event1 = MagicMock()
        mock_event1.data = json.dumps({"choices": [{"delta": {"content": "part1"}}]})
        mock_event2 = MagicMock()
        mock_event2.data = json.dumps({"choices": [{"delta": {"content": "part2"}}]})
        mock_event_done = MagicMock()
        mock_event_done.data = "[DONE]"

        # Setting up a test stream
        test_stream = [mock_event1, mock_event2, mock_event_done]
        mock_sse_client.return_value.events = MagicMock(return_value=iter(test_stream))

        # Execution
        client = MistralClient(model_name="test_model", temperature = 0.0)
        messages = [{"role": "user", "content": "hello"}]
        stream = client.perform_stream_request(messages)

        # Verification: Extracting and verifying the stream response
        responses = []
        for event in stream.events():
            if event.data != "[DONE]":
                event_data = json.loads(event.data)
                if "choices" in event_data and len(event_data["choices"]) > 0:
                    response_content = event_data["choices"][0]["delta"].get("content", "")
                    responses.append(response_content)

        self.assertEqual(responses, ["part1", "part2"])

    @patch("tinychat.llms.mistral.requests.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Setup: Mocking the response with an error status code
        mock_response = Mock(spec=Response)
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        # Execution
        client = MistralClient(model_name="test_model", temperature = 0.0)
        messages = [{"role": "user", "content": "hello"}]

        # Verification: Expecting a ValueError on error response
        with self.assertRaises(ValueError) as context:
            next(client.perform_stream_request(messages))  # type: ignore
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
```