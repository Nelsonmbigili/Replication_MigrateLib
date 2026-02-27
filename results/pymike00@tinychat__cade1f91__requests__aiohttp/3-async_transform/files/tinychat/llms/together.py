import json
from typing import AsyncGenerator

import aiohttp
from sseclient import SSEClient  # This is no longer used but kept for compatibility with other parts of the app.

from tinychat.llms.base import BaseLLMClient
from tinychat.settings import TOGETHER_API_KEY_NAME


class TogetherClient(BaseLLMClient):
    """
    Simple client for interacting with the Together API.
    Currently only supports the chat completions endpoint.

    :param model_name: The name of the model to be used for chat requests.
    """

    TOGHETER_COMPLETION_API_URL = "https://api.together.xyz/v1/chat/completions"

    def __init__(self, model_name: str, temperature: float) -> None:
        super().__init__(api_key_name=TOGETHER_API_KEY_NAME)
        self.model_name = model_name
        self.temperature = temperature

    async def perform_stream_request(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        """
        Perform a streaming request to the Together API.

        :param messages: The list of messages to send to the API.
        :return: An asynchronous generator yielding streamed events.
        """
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.TOGHETER_COMPLETION_API_URL,
                headers=self.default_headers(),  # type: ignore
                json=data,
            ) as response:
                if response.status != 200:
                    raise ValueError(
                        f"Server responded with an error. Status Code: {response.status}"
                    )
                async for line in response.content:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line:
                        yield decoded_line


class TogetherHandler:
    """
    Handler class to interact with the Together models.

    Returns chat responses and stores the chat history.
    """

    def __init__(self, model_name: str, temperature: float = 0.0):
        self._messages = []
        self._client = TogetherClient(model_name, temperature)
    
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
        :return: An asynchronous generator yielding the model's response in streamed parts.
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
