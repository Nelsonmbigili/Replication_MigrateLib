import json
from typing import Generator
import pycurl
from io import BytesIO

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
    ) -> str:
        data = {
            "chat_history": chat_history,
            "message": user_input,
            "temperature": self.temperature,
            "stream": True,
        }
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, self.COHERE_CHAT_API_URL)
        curl.setopt(curl.HTTPHEADER, [f"Authorization: {self.default_headers()['Authorization']}", "Content-Type: application/json"])
        curl.setopt(curl.POSTFIELDS, json.dumps(data))
        curl.setopt(curl.WRITEFUNCTION, buffer.write)
        curl.setopt(curl.NOBODY, False)

        try:
            curl.perform()
            response_code = curl.getinfo(curl.RESPONSE_CODE)
            if response_code != 200:
                raise ValueError(f"Server responded with error: {response_code}")
            response_data = buffer.getvalue().decode("utf-8")
            return response_data
        except pycurl.error as e:
            raise ValueError(f"An error occurred: {e}")
        finally:
            curl.close()

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
        for response_piece in stream.splitlines():  # type: ignore
            try:
                data = json.loads(response_piece)
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
