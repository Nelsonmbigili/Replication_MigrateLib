### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Asynchronous Nature of `treq`**: The `treq` library is asynchronous, so the `perform_stream_request` method was modified to be asynchronous (`async def`) and to use `await` for the `treq` calls.
2. **HTTP POST Request**: The `requests.post` call was replaced with `treq.post`. The `headers` and `json` parameters were passed in the same way, but `treq` requires the `json` data to be encoded using `json.dumps`.
3. **Streaming Response**: The `treq` library provides an asynchronous way to handle streaming responses. The `response.content` was replaced with an asynchronous iterator using `response.iter_chunks`.
4. **SSEClient Integration**: Since `SSEClient` is synchronous, it was replaced with a custom asynchronous generator to handle Server-Sent Events (SSE) using the streamed chunks from `treq`.
5. **Calling the Stream**: The `stream_response` method was updated to handle the asynchronous nature of the `perform_stream_request` method and the custom SSE generator.

### Modified Code
```python
import json
from typing import Generator, AsyncGenerator

import treq
from sseclient import Event  # Using Event class from sseclient for compatibility

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

    async def perform_stream_request(self, messages: list[dict]) -> AsyncGenerator[Event, None]:
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
        }
        response = await treq.post(
            self.MISTRAL_COMPLETION_API_URL,
            headers=self.default_headers(),  # type: ignore
            json=json.dumps(data),
        )
        if response.code != 200:
            raise ValueError(
                f"Server responded with an error. Status Code: {response.code}"
            )

        # Asynchronous generator to handle SSE events
        async for chunk in response.iter_chunks():
            if chunk:
                for line in chunk.splitlines():
                    if line.strip():  # Ignore empty lines
                        yield Event(data=line.decode("utf-8"))


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

    async def export_conversation(self) -> str:
        string_conversation = ""
        for message in self._messages:
            if message["role"] == "user":
                if string_conversation != "":
                    string_conversation += "\n\n"
                string_conversation += f"You: {message['content']}"
            else:
                string_conversation += f"LLM: {message['content']}"
        return string_conversation

    async def stream_response(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        Yield stream responses from the client as they are received.

        This method sends the user input to the client and then yields each piece
        of the language model's response as it is received in real-time. After the
        streaming is complete, it updates the message list with the user input and
        the full language model response.

        :param user_input: The input string from the user to be sent to the model.
        :return: An asynchronous generator yielding the model's response in streamed parts.
        """
        self._messages.append({"role": "user", "content": user_input})
        stream = self._client.perform_stream_request(self._messages)
        lm_response = ""
        async for event in stream:
            if event.data != "[DONE]":
                json_load = json.loads(event.data)["choices"][0]["delta"]
                if "content" in json_load.keys():
                    response_piece = json_load["content"]
                    lm_response += response_piece
                    yield response_piece
        self._messages.append({"role": "assistant", "content": lm_response})
```

### Key Notes
1. **Asynchronous Generators**: The `perform_stream_request` and `stream_response` methods are now asynchronous and use `async for` to handle streaming data.
2. **Custom SSE Handling**: Since `treq` does not natively support SSE, a custom asynchronous generator was implemented to parse the streamed chunks into SSE events.
3. **Compatibility**: The `Event` class from `sseclient` was reused to maintain compatibility with the rest of the application.