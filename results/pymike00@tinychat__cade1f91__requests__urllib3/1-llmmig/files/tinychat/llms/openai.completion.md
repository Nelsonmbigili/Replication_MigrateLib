### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Replace `requests.post` with `urllib3.PoolManager.request`**:
   - `urllib3` does not have a `post` method like `requests`. Instead, we use the `request` method of `urllib3.PoolManager` and specify the HTTP method (`POST` in this case).
   - The `headers` and `body` parameters are passed explicitly to the `request` method.
   - JSON data is serialized using `json.dumps` and passed as the `body` parameter.
2. **Handle Streaming**:
   - `urllib3` supports streaming responses via the `preload_content=False` parameter in the `request` method. This allows us to iterate over the response data in chunks.
   - The `SSEClient` is updated to work with the `urllib3` response object.
3. **Error Handling**:
   - The status code is checked using the `status` attribute of the `urllib3` response object instead of `response.status_code`.

Below is the modified code.

---

### Modified Code
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
        self.http = urllib3.PoolManager()  # Initialize urllib3 PoolManager

    def perform_stream_request(self, messages: list[dict]) -> SSEClient:
        # info: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
        }
        # Serialize JSON data
        body = json.dumps(data)
        # Make the POST request with streaming enabled
        response = self.http.request(
            "POST",
            self.OPENAI_COMPLETION_API_URL,
            headers=self.default_headers(),  # type: ignore
            body=body,
            preload_content=False,  # Enable streaming
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

---

### Key Points
- The `urllib3.PoolManager` is used to manage HTTP connections.
- The `request` method is used for making HTTP requests, with `preload_content=False` to enable streaming.
- JSON data is serialized manually using `json.dumps` and passed as the `body` parameter.
- The `status` attribute of the `urllib3` response object is used to check the HTTP status code.