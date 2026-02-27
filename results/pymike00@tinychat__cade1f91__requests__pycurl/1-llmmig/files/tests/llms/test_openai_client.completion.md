### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.post` with `pycurl`**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with the necessary options (e.g., URL, HTTP headers, POST data).
   - The response body is captured using a `BytesIO` object from the `io` module.
2. **Mocking `pycurl`**:
   - Since `pycurl` does not have a direct equivalent to `requests.models.Response`, the mocking strategy was adjusted to simulate the behavior of `pycurl` by capturing the response in a `BytesIO` object.
3. **Error Handling**:
   - `pycurl` raises exceptions for HTTP errors, so the error handling logic was updated to check the HTTP status code explicitly.
4. **Streaming**:
   - The streaming logic remains unchanged, as it is handled by the `SSEClient` and not directly by `requests`.

Below is the modified code:

---

### Modified Code:
```python
import json
import unittest
from unittest.mock import MagicMock, Mock, patch
from io import BytesIO

import pycurl

from tinychat.llms.openai import OpenAIClient


class TestOpenAIClientStreaming(unittest.TestCase):

    @patch("tinychat.llms.openai.pycurl.Curl")
    @patch("tinychat.llms.openai.SSEClient")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_success(
        self, mock_api_key, mock_sse_client, mock_curl
    ):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking pycurl and the response
        mock_curl_instance = Mock()
        mock_curl.return_value = mock_curl_instance

        # Simulating a successful HTTP response
        response_body = BytesIO()
        response_body.write(b'{"choices": [{"delta": {"content": "part1"}}]}')
        response_body.seek(0)
        mock_curl_instance.perform.side_effect = lambda: response_body.write(
            b'{"choices": [{"delta": {"content": "part2"}}]}'
        )
        mock_curl_instance.getinfo.return_value = 200  # HTTP status code

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

        client = OpenAIClient(model_name="test_model", temperature=0.0)
        messages = [{"role": "user", "content": "hello"}]
        stream = client.perform_stream_request(messages)

        # Extracting and verifying the stream response
        responses = []
        for event in stream.events():
            if event.data != "[DONE]":
                event_data = json.loads(event.data)
                if "choices" in event_data and len(event_data["choices"]) > 0:
                    response_content = event_data["choices"][0]["delta"].get(
                        "content", ""
                    )
                    responses.append(response_content)

        self.assertEqual(responses, ["part1", "part2"])

    @patch("tinychat.llms.openai.pycurl.Curl")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_curl):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Mocking pycurl and simulating an error response
        mock_curl_instance = Mock()
        mock_curl.return_value = mock_curl_instance

        response_body = BytesIO()
        response_body.write(b"Error")
        response_body.seek(0)
        mock_curl_instance.perform.side_effect = lambda: None
        mock_curl_instance.getinfo.return_value = 400  # HTTP status code

        client = OpenAIClient(model_name="test_model", temperature=0.0)
        messages = [{"role": "user", "content": "hello"}]

        with self.assertRaises(ValueError) as context:
            next(client.perform_stream_request(messages))  # type: ignore
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
```

---

### Key Notes:
1. The `pycurl.Curl` object is mocked to simulate HTTP requests and responses.
2. The `BytesIO` object is used to capture the response body, as `pycurl` writes directly to a file-like object.
3. The `SSEClient` logic remains unchanged, as it is independent of the HTTP client library.
4. The error handling logic explicitly checks the HTTP status code using `pycurl.Curl.getinfo`.