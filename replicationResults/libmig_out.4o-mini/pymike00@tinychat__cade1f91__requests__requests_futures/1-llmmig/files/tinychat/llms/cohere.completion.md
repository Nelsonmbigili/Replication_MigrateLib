### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The import statement for `requests` was replaced with `from requests_futures.sessions import FuturesSession`.
2. **Session Initialization**: Instead of using `requests.post`, a `FuturesSession` object was created, which allows for asynchronous requests.
3. **Asynchronous Request Handling**: The `post` method of the `FuturesSession` was used to send the request, which returns a `Future` object. This object is then used to retrieve the response.
4. **Response Handling**: The response is accessed using the `result()` method of the `Future` object, which blocks until the response is available.

Here is the modified code:

```python
import json
from typing import Generator

from requests_futures.sessions import FuturesSession

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
        self.session = FuturesSession()  # Initialize FuturesSession

    def perform_stream_request(
        self, user_input: str, chat_history: list[dict]
    ) -> str:  # Change return type to str for streaming
        data = {
            "chat_history": chat_history,
            "message": user_input,
            "temperature": self.temperature,
            "stream": True,
        }
        future_response = self.session.post(  # Use FuturesSession to post
            self.COHERE_CHAT_API_URL,
            headers=self.default_headers(),
            json=data,
            stream=True,
        )
        response = future_response.result()  # Get the response from the Future
        if response.status_code != 200:
            raise ValueError(f"Server responded with error: {response.status_code}")
        try:
            return response.iter_content()  # Return the stream content
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
        for response_piece in stream:  # type: ignore
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

This code now uses `requests_futures` to handle asynchronous HTTP requests while maintaining the original structure and functionality.