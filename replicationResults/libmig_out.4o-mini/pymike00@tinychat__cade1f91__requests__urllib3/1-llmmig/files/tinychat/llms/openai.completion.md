### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` library is a higher-level abstraction over HTTP requests, while `urllib3` is a lower-level library that requires more manual handling of requests and responses.

2. **Creating a Pool Manager**: A `PoolManager` instance from `urllib3` was created to handle the connection pool and make requests.

3. **Making the POST Request**: The `requests.post` method was replaced with `http.request('POST', ...)` from `urllib3`, which requires specifying the method, URL, headers, and body separately.

4. **Handling the Response**: The response handling was adjusted to work with `urllib3`'s response object, which does not have a `status_code` attribute but instead uses `status`.

5. **Reading the Response**: The response body is read using `response.data`, which returns the raw bytes. This needs to be decoded to a string for JSON parsing.

Here is the modified code:

```python
import json
from typing import Generator

import urllib3
from sseclient import SSEClient

from tinychat.llms.base import BaseLLMClient
from tinychat.settings import OPENAI_API_KEY_NAME


class OpenAIClient(BaseLLMClient):
    """
    Simple client for interacting with the OpenAI API.
    Currently only supports the chat completions endpoint.

    :param model_name: The name of the model to be used for chat requests.
    """

    OPENAI_COMPLETION_API_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(self, model_name: str, temperature: float) -> None:
        super().__init__(api_key_name=OPENAI_API_KEY_NAME)
        self.model_name = model_name
        self.temperature = temperature
        self.http = urllib3.PoolManager()

    def perform_stream_request(self, messages: list[dict]) -> SSEClient:
        # info: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
        }
        response = self.http.request(
            'POST',
            self.OPENAI_COMPLETION_API_URL,
            headers=self.default_headers(),  # type: ignore
            body=json.dumps(data),
            preload_content=False,
        )
        if response.status != 200:
            raise ValueError(
                f"Server responded with an error. Status Code: {response.status}"
            )
        return SSEClient(event_source=response)  # type: ignore


class OpenAIHandler:
    """
    Handler class to interact with the OpenAI models.

    Returns chat responses and stores the chat history.
    """

    def __init__(self, model_name: str, temperature: float = 0.0):
        self._messages = []
        self._client = OpenAIClient(model_name, temperature)

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