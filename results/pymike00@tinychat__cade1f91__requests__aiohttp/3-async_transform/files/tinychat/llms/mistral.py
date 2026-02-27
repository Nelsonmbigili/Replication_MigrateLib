import json
from typing import Generator, AsyncGenerator

import aiohttp
from sseclient import SSEClient  # Removed usage but kept import for compatibility with other parts of the app

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

    async def perform_stream_request(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.MISTRAL_COMPLETION_API_URL,
                headers=self.default_headers(),  # type: ignore
                json=data,
            ) as response:
                if response.status != 200:
                    raise ValueError(
                        f"Server responded with an error. Status Code: {response.status}"
                    )
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        yield chunk.decode("utf-8")


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
        async for chunk in self._client.perform_stream_request(self._messages):
            for line in chunk.splitlines():
                if line.strip() == "[DONE]":
                    break
                event = json.loads(line)
                if "choices" in event and "delta" in event["choices"][0]:
                    json_load = event["choices"][0]["delta"]
                    if "content" in json_load.keys():
                        response_piece = json_load["content"]
                        lm_response += response_piece
                        yield response_piece
        self._messages.append({"role": "assistant", "content": lm_response})
