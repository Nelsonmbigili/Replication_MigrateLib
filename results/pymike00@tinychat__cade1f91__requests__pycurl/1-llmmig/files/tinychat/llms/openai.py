import json
from typing import Generator
import pycurl
from io import BytesIO

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

    def perform_stream_request(self, messages: list[dict]) -> SSEClient:
        # info: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
        }
        # Convert the data to JSON
        json_data = json.dumps(data)

        # Prepare a buffer to capture the response
        response_buffer = BytesIO()

        # Initialize pycurl
        curl = pycurl.Curl()
        curl.setopt(curl.URL, self.OPENAI_COMPLETION_API_URL)
        curl.setopt(curl.HTTPHEADER, [f"Authorization: Bearer {self.api_key}", "Content-Type: application/json"])
        curl.setopt(curl.POST, 1)
        curl.setopt(curl.POSTFIELDS, json_data)
        curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
        curl.setopt(curl.VERBOSE, False)

        # Perform the request
        curl.perform()

        # Check the HTTP status code
        status_code = curl.getinfo(curl.RESPONSE_CODE)
        if status_code != 200:
            curl.close()
            raise ValueError(f"Server responded with an error. Status Code: {status_code}")

        # Close the curl object
        curl.close()

        # Pass the response to SSEClient
        response_data = response_buffer.getvalue().decode("utf-8")
        return SSEClient(event_source=response_data)  # type: ignore


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
