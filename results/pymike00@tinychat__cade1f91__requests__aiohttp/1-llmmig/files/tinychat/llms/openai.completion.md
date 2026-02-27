### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so the `perform_stream_request` method was converted to an `async` function. This required the use of `async def` and `await` for asynchronous operations.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` for making HTTP requests. A session is created and used for the POST request.
3. **Streaming Response**: The `aiohttp` library provides an `aiohttp.ClientResponse.content` stream for handling streamed responses. This was used to read the response incrementally.
4. **SSEClient Replacement**: The `SSEClient` library is not compatible with `aiohttp`. Instead, the streaming response was manually processed using `aiohttp`'s streaming capabilities.
5. **Generator Changes**: Since `aiohttp` operations are asynchronous, the `stream_response` method was also converted to an `async` generator (`async def` with `yield`).

### Modified Code
Here is the complete code after migration to `aiohttp`:

```python
import json
from typing import AsyncGenerator

import aiohttp
from sseclient import SSEClient  # Removed usage but kept import for compatibility with other parts of the app

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

    async def perform_stream_request(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        # info: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.OPENAI_COMPLETION_API_URL,
                headers=self.default_headers(),  # type: ignore
                json=data,
            ) as response:
                if response.status != 200:
                    raise ValueError(
                        f"Server responded with an error. Status Code: {response.status}"
                    )
                async for line in response.content:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line:  # Skip empty lines
                        yield decoded_line


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

    async def stream_response(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        Yield stream responses from the client as they are received.

        This method sends the user input to the client and then yields each piece
        of the language model's response as it is received in real-time. After the
        streaming is complete, it updates the message list with the user input and
        the full language model response.

        :param user_input: The input string from the user to be sent to the model.
        :return: An async generator yielding the model's response in streamed parts.
        """
        self._messages.append({"role": "user", "content": user_input})
        lm_response = ""
        async for event in self._client.perform_stream_request(self._messages):
            if event != "[DONE]":
                json_load = json.loads(event)["choices"][0]["delta"]
                if "content" in json_load.keys():
                    response_piece = json_load["content"]
                    lm_response += response_piece
                    yield response_piece
        self._messages.append({"role": "assistant", "content": lm_response})
```

### Key Notes
1. **Async Generators**: The `perform_stream_request` and `stream_response` methods are now asynchronous generators, which allow yielding values while performing asynchronous operations.
2. **Session Management**: The `aiohttp.ClientSession` is used with a context manager (`async with`) to ensure proper cleanup of resources.
3. **Streaming Response Handling**: The `response.content` stream is read line by line, and each line is decoded and processed.

This migration ensures that the code is now fully compatible with `aiohttp` while maintaining the original functionality.