### Explanation of Changes

To migrate the code from the `requests` library to `urllib3`, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was removed, and `urllib3` was imported instead.
2. **HTTP Connection Management**: `urllib3` requires explicit creation of an `HTTPConnectionPool` or `PoolManager` for making HTTP requests. A `PoolManager` was used for simplicity.
3. **POST Request**: The `requests.post` method was replaced with `urllib3.PoolManager.request` using the `POST` method. The `json` parameter in `requests` was replaced with `body` (JSON-encoded manually using `json.dumps`).
4. **Headers**: The `headers` parameter remains the same, as both libraries support it in a similar way.
5. **Streaming Response**: `urllib3` provides a `stream()` method for streaming responses. This was used to replace the `stream=True` functionality of `requests`.
6. **Error Handling**: The `status_code` attribute in `requests` was replaced with `response.status` in `urllib3`.
7. **Response Iteration**: The `iter_content` method in `requests` was replaced with `response.stream()` in `urllib3`.

### Modified Code

```python
import json
from typing import Generator

import urllib3

from tinychat.llms.base import BaseLLMClient
from tinychat.settings import COHERE_API_KEY_NAME


class CohereClient(BaseLLMClient):
    """
    Cohere chat client.
    """

    COHERE_CHAT_API_URL = "https://api.cohere.ai/v1/chat"

    def __init__(self, temperature: float) -> None:
        super().__init__(api_key_name=COHERE_API_KEY_NAME)
        self.temperature = temperature
        self.http = urllib3.PoolManager()  # Create a PoolManager for HTTP requests

    def perform_stream_request(
        self, user_input: str, chat_history: list[dict]
    ) -> urllib3.response.HTTPResponse:
        data = {
            "chat_history": chat_history,
            "message": user_input,
            "temperature": self.temperature,
            "stream": True,
        }
        response = self.http.request(
            "POST",
            self.COHERE_CHAT_API_URL,
            headers=self.default_headers(),
            body=json.dumps(data),  # Manually encode the JSON body
            preload_content=False,  # Disable preloading to enable streaming
        )
        if response.status != 200:  # Check the status code
            raise ValueError(f"Server responded with error: {response.status}")
        try:
            return response
        except ValueError:
            raise ValueError("Invalid response format received from server.")


class CohereHandler:
    """
    Handler class to interact with the Cohere models.

    Returns chat responses and stores the chat history.

    TODO: add chat message dataclass so that we can enforce validation of
    message format that is needed for working client requests to the API?
    """

    def __init__(self, temperature: float = 0.0):
        self._chat_history = []
        self._client = CohereClient(temperature)

    def export_conversation(self) -> str:
        string_conversation = ""
        for message in self._chat_history:
            if message["role"] == "User":
                if string_conversation != "":
                    string_conversation += "\n\n"
                string_conversation += f"You: {message['message']}"
            else:
                string_conversation += f"LLM: {message['message']}"
        return string_conversation

    def stream_response(self, user_input: str) -> Generator[str, None, None]:
        """
        Yield stream responses from the client as they are received.

        This method sends the user input to the client and then yields each piece
        of the language model's response as it is received in real-time. After the
        streaming is complete, it updates the message list with the user input and
        the full language model response.

        :param user_input: The input string from the user to be sent to the model.
        :return: A generator yielding the model's response in streamed parts.
        """
        self._chat_history.append({"role": "User", "message": user_input})
        stream = self._client.perform_stream_request(user_input, self._chat_history)
        lm_response = ""
        for response_piece in stream.stream():  # Use stream() to iterate over chunks
            try:
                data = json.loads(response_piece.decode("utf-8"))
            except ValueError as e:
                # HACK. Cohere's stream last response should include the whole response but for some reasons it comes back broken
                # Info: https://docs.cohere.com/reference/chat
                continue
            if not "event_type" in data.keys():
                continue
            if data["event_type"] == "text-generation":
                lm_response += data["text"]
                yield data["text"]
        self._chat_history.append({"role": "Chatbot", "message": lm_response})
        stream.release_conn()  # Release the connection after streaming is complete
```

### Key Notes
- The `urllib3.PoolManager` is used to manage HTTP connections.
- The `preload_content=False` parameter ensures that the response is streamed instead of being fully loaded into memory.
- The `stream()` method of the `HTTPResponse` object is used to iterate over the response chunks.
- The `release_conn()` method is called to release the connection back to the pool after streaming is complete.