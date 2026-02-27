### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class provided by `requests_futures`.
2. **Mocking Adjustments**: Updated the `@patch` decorators to mock `requests_futures.sessions.FuturesSession.post` instead of `requests.post`.
3. **Response Handling**: Since `requests_futures` returns a `Future` object when making asynchronous requests, the `result()` method is used to retrieve the actual `Response` object in the test cases.
4. **Mocking Futures**: Updated the mocked `post` method to return a `Future` object with a mocked `Response` as its result.

### Modified Code:
```python
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
```

### Key Points:
- The `FuturesSession` class from `requests_futures` is used to handle asynchronous HTTP requests.
- The `result()` method is called on the `Future` object returned by `FuturesSession.post` to retrieve the actual `Response` object.
- Mocking is adjusted to simulate the behavior of `FuturesSession.post` and its returned `Future` object.