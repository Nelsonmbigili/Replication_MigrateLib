import os
from abc import ABC, abstractmethod

from libmig.mig.mig_error import MigError, ErrorCode


class LLMClient(ABC):
    @abstractmethod
    def request(self, messages: list) -> str:
        pass


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def request(self, messages: list) -> str:
        from openai import OpenAI, BadRequestError, APITimeoutError
        # for some reason, if I move this import to the top of the file, the program crashes in debug mode

        client = OpenAI(api_key=self.api_key)

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                response_format={
                    "type": "text"
                },
                timeout=10 * 60  # 10 minutes
            )
        except BadRequestError as e:
            if "This model's maximum context length is" in e.message:
                raise MigError(ErrorCode.LLM_TOKEN_LIMIT_EXCEEDED, "input token limit exceeded") from e
            raise e
        except APITimeoutError as e:
            raise MigError(ErrorCode.LLM_API_TIMEOUT, "API timeout") from e

        choices = response.choices
        if not choices:
            raise MigError(ErrorCode.LLM_NO_RESPONSE, "no response from OpenAI")
        if len(choices) > 1:
            raise MigError(ErrorCode.LLM_MORE_THAN_ONE_RESPONSE, "more than one response from OpenAI")

        choice = choices[0]
        if choice.finish_reason != "stop":
            if choice.finish_reason == "length":
                raise MigError(ErrorCode.LLM_TOKEN_LIMIT_EXCEEDED, "output token limit exceeded")
            raise MigError(ErrorCode.LLM_UNEXPECTED_FINISH_REASON, "finish reason: " + choice.finish_reason)

        return choice.message.content
