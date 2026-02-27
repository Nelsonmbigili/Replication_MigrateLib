### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures`.
2. **Session Usage**: `requests_futures` provides asynchronous request capabilities via `FuturesSession`. Replaced the `requests.post` call with `FuturesSession` and used its `post` method.
3. **Response Handling**: Since `FuturesSession.post` returns a `Future` object, the `.result()` method is called to get the actual response object. This ensures compatibility with the existing synchronous code.
4. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the larger application.

### Modified Code:
```python
import json
from typing import Generator

from requests_futures.sessions import FuturesSession
from sseclient import SSEClient

from tinychat.llms.base import BaseLLMClient
from tinychat.settings import MISTRAL_API_KEY_NAME


class MistralClient(BaseLLMClient):
    """
    Mistral chat client.
    """

    MISTRAL_COMPLETION_API_URL = "https://api.mistral.ai/v1/chat/completions"

    def __init__(self, model_name: str, temperature: float) -> None:
        super().__init__(api_key_name=MISTRAL_API_KEY_NAME)
        self.model_name = model_name
        self.temperature = temperature
        self.session = FuturesSession()  # Initialize a FuturesSession for async requests

    def perform_stream_request(self, messages: list[dict]) -> SSEClient:
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
        }
        future = self.session.post(
            self.MISTRAL_COMPLETION_API_URL,
            headers=self.default_headers(),  # type: ignore
            json=data,
            stream=True,
        )
        response = future.result()  # Wait for the response to complete
        if response.status_code != 200:
            raise ValueError(
                f"Server responded with an error. Status Code: {response.status_code}"
            )
        return SSEClient(event_source=response)  # type: ignore


class MistralHandler:
    """
    Handler class to interact with the Mistral models via API.

    Returns chat responses and stores the chat history.

    TODO: add chat message dataclass so that we can enforce validation of
    message format that is needed for working client requests to the API?
    """

    def __init__(self, model_name: str, temperature: float = 0.0):
        self._messages = []
        self._client = MistralClient(model_name, temperature)

    def export_conversation(self) -> str:
        string_conversation = ""
        for message in self._messages:
            if message["role"] == "user":
                if string_conversation != "":
                    string_conversation += "\n\n"
                string_conversation += f"You: {message['content']}"
            else:
                string_conversation += f"LLM: {message['content']}"
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
        self._messages.append({"role": "user", "content": user_input})
        stream = self._client.perform_stream_request(self._messages)
        lm_response = ""
        for event in stream.events():  # type: ignore
            if event.data != "[DONE]":
                json_load = json.loads(event.data)["choices"][0]["delta"]
                if "content" in json_load.keys():
                    response_piece = json_load["content"]
                    lm_response += response_piece
                    yield response_piece
        self._messages.append({"role": "assistant", "content": lm_response})
```

### Summary of Changes:
- Replaced `requests` with `requests_futures`.
- Used `FuturesSession` to make asynchronous requests.
- Called `.result()` on the `Future` object to retrieve the response synchronously, ensuring compatibility with the existing code.