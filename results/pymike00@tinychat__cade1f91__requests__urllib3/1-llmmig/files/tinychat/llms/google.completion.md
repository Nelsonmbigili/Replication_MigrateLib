### Explanation of Changes
To migrate the code from the `requests` library to `urllib3`, the following changes were made:
1. **Replaced `requests.post` with `urllib3.PoolManager.request`**:
   - `urllib3` does not have a direct `post` method like `requests`. Instead, we use the `request` method of `urllib3.PoolManager` and specify the HTTP method (`POST`).
   - The `json` parameter in `requests.post` is replaced with `body=json.dumps(data)` and the `Content-Type` header is explicitly set to `application/json`.
2. **Stream Handling**:
   - `requests` supports streaming responses with the `stream=True` parameter. In `urllib3`, streaming is handled by reading the response data in chunks using the `HTTPResponse.stream()` method.
3. **Error Handling**:
   - `requests` raises exceptions for HTTP errors automatically. In `urllib3`, we need to manually check the status code and raise an error if necessary.
4. **Session Management**:
   - `urllib3` uses a `PoolManager` for managing connections. A `PoolManager` instance is created and reused for making HTTP requests.

### Modified Code
Here is the updated code using `urllib3` version 2.1.0:

```python
import json
from typing import Generator

import urllib3
from sseclient import SSEClient

from tinychat.llms.base import BaseLLMClient
from tinychat.settings import GOOGLE_API_KEY_NAME


class GoogleAIClient(BaseLLMClient):
    """
    Simple client for interacting with the Google API.
    Currently only supports the chat completions endpoint.

    :param model_name: The name of the model to be used for chat requests.
    """

    BASE_GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:streamGenerateContent"
    SAFETY_SETTINGS = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
    ]

    def __init__(self, temperature: float) -> None:
        super().__init__(api_key_name=GOOGLE_API_KEY_NAME)
        self.generation_config = {
            "stopSequences": ["Title"],
            "temperature": temperature,
            "maxOutputTokens": 4096,
            "topP": 0.8,
            "topK": 10,
        }
        self.http = urllib3.PoolManager()  # Initialize a PoolManager for HTTP requests

    @property
    def gemini_endpoint(self):
        return f"{self.BASE_GEMINI_ENDPOINT}?alt=sse&key={self.api_key}"

    @property
    def gemini_headers(self):
        return {"Content-Type": "application/json"}

    def perform_stream_request(self, messages: list[dict]) -> SSEClient:
        # info: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
        data = {
            "contents": messages,
            "safetySettings": self.SAFETY_SETTINGS,
            "generationConfig": self.generation_config,
        }
        # Make the POST request using urllib3
        response = self.http.request(
            "POST",
            self.gemini_endpoint,
            headers=self.gemini_headers,  # type: ignore
            body=json.dumps(data),  # Serialize the data to JSON
            preload_content=False,  # Disable automatic content loading for streaming
        )

        # Check for HTTP errors
        if response.status != 200:
            response_data = response.data.decode("utf-8")
            raise ValueError(
                f"Server responded with an error. Status Code: {response.status}, Response: {response_data}"
            )

        # Return an SSEClient instance for streaming
        return SSEClient(event_source=response)  # type: ignore


class GoogleAIHandler:
    """
    Handler class to interact with the Google AI models.

    Returns chat responses and stores the chat history.

    TODO: add chat message dataclass so that we can enforce validation of
    message format that is needed for working client requests to the API?
    """

    def __init__(self, temperature: float = 0.0):
        self._messages = []
        self._client = GoogleAIClient(temperature)

    def export_conversation(self) -> str:
        string_conversation = ""
        for message in self._messages:
            print(message)
            if message["role"] == "user":
                if string_conversation != "":
                    string_conversation += "\n\n"
                string_conversation += f"You: {message['parts'][0]['text']}"
            else:
                string_conversation += f"LLM: {message['parts'][0]['text']}"
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
        self._messages.append({"parts": [{"text": user_input}], "role": "user"})
        stream = self._client.perform_stream_request(self._messages)
        lm_response = ""
        for event in stream.events():  # type: ignore
            event_data = json.loads(event.data)
            # TODO: improve
            if "candidates" in event_data:
                response_piece = event_data["candidates"][0]["content"]["parts"][0][
                    "text"
                ]
                lm_response += response_piece
                yield response_piece
        self._messages.append({"parts": [{"text": lm_response}], "role": "model"})
```

### Key Notes
- The `urllib3.PoolManager` instance is reused for all HTTP requests, which is efficient and aligns with `urllib3`'s design.
- The `preload_content=False` parameter ensures that the response is streamed and not fully loaded into memory.
- The `response.data.decode("utf-8")` is used to decode the response body in case of errors.