### Explanation of Changes
To migrate the code from `requests` to `httpx`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `httpx`.
2. **HTTP Client**: Replaced `requests.post` with `httpx.post`. The syntax for `httpx.post` is similar to `requests.post`, so only minor adjustments were needed.
3. **Streaming Response**: In `httpx`, the streaming response is handled using an asynchronous iterator (`response.aiter_text()` or `response.aiter_bytes()`). Since the original code uses synchronous streaming, I used `response.iter_bytes()` to maintain compatibility.
4. **Response Handling**: Adjusted the response handling to work with `httpx`'s API. For example, `response.iter_content()` in `requests` was replaced with `response.iter_bytes()` in `httpx`.
5. **Error Handling**: The error handling logic remains the same, as `httpx` also provides `response.status_code` for checking HTTP status codes.

### Modified Code
Here is the updated code using `httpx` version 0.28.1:

```python
import json
from typing import Generator

import httpx

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

    def perform_stream_request(
        self, user_input: str, chat_history: list[dict]
    ) -> httpx.Response:
        data = {
            "chat_history": chat_history,
            "message": user_input,
            "temperature": self.temperature,
            "stream": True,
        }
        response = httpx.post(
            self.COHERE_CHAT_API_URL,
            headers=self.default_headers(),
            json=data,
            stream=True,
        )
        if response.status_code != 200:
            raise ValueError(f"Server responded with error: {response.status_code}")
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
        for response_piece in stream.iter_bytes():  # Changed to httpx's iter_bytes
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
```

### Summary of Changes
- Replaced `requests` with `httpx`.
- Used `httpx.post` for making HTTP POST requests.
- Replaced `response.iter_content()` with `response.iter_bytes()` for streaming responses.
- Kept the rest of the logic intact to ensure compatibility with the existing application.