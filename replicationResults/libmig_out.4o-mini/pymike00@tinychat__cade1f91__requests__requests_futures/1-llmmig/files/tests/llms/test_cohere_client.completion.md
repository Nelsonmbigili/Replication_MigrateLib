### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The import statement for `requests` was replaced with `from requests_futures.sessions import FuturesSession`. This allows us to use the `FuturesSession` class, which supports asynchronous requests.
  
2. **Session Initialization**: Instead of using `requests.post`, we create an instance of `FuturesSession` and use its `post` method to make the HTTP requests.

3. **Mocking Changes**: The mock for `post` was updated to reflect the new session method. The mock now needs to be set up for the `FuturesSession` instead of the `requests` module.

4. **Response Handling**: The response handling remains similar, but we need to ensure that we are working with the correct response type from the `FuturesSession`.

Here is the modified code:

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
        
        mock_response = Mock(spec=Mock)
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        response = client.perform_stream_request("how are you?", chat_history)
        self.assertIsInstance(response, Mock)
        self.assertEqual(response.status_code, 200)

    @patch("tinychat.llms.cohere.FuturesSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        mock_response = Mock(spec=Mock)
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        client = CohereClient(temperature=0.0)
        chat_history = [
            {"role": "User", "message": "hello"},
            {"role": "Chatbot", "message": "hello!"},
        ]
        with self.assertRaises(ValueError) as context:
            client.perform_stream_request("how are you?", chat_history)
        self.assertIn("Server responded with error: 400", str(context.exception))
``` 

This code now uses `requests_futures` for making asynchronous HTTP requests while maintaining the original structure and functionality of the tests.