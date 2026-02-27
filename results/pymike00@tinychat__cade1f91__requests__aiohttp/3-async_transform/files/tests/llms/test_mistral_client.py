import json
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import asyncio

from aiohttp import ClientResponse

from tinychat.llms.mistral import MistralClient
import pytest


class TestMistralClientStreaming(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    @patch("tinychat.llms.mistral.aiohttp.ClientSession.post")
    @patch("tinychat.llms.mistral.SSEClient")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    async def test_perform_stream_request_success(self, mock_api_key, mock_sse_client, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here
        
        # Setup: Mocking SSEClient and the response
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response

        # Creating mock events
        mock_event1 = MagicMock()
        mock_event1.data = json.dumps({"choices": [{"delta": {"content": "part1"}}]})
        mock_event2 = MagicMock()
        mock_event2.data = json.dumps({"choices": [{"delta": {"content": "part2"}}]})
        mock_event_done = MagicMock()
        mock_event_done.data = "[DONE]"

        # Setting up a test stream
        test_stream = [mock_event1, mock_event2, mock_event_done]
        mock_sse_client.return_value.events = MagicMock(return_value=iter(test_stream))

        # Execution
        client = MistralClient(model_name="test_model", temperature=0.0)
        messages = [{"role": "user", "content": "hello"}]
        stream = await client.perform_stream_request(messages)

        # Verification: Extracting and verifying the stream response
        responses = []
        async for event in stream.events():
            if event.data != "[DONE]":
                event_data = json.loads(event.data)
                if "choices" in event_data and len(event_data["choices"]) > 0:
                    response_content = event_data["choices"][0]["delta"].get("content", "")
                    responses.append(response_content)

        self.assertEqual(responses, ["part1", "part2"])

    @pytest.mark.asyncio
    @patch("tinychat.llms.mistral.aiohttp.ClientSession.post")
    @patch("tinychat.llms.base.BaseLLMClient.api_key", new_callable=MagicMock)
    async def test_perform_stream_request_failure(self, mock_api_key, mock_post):
        # Setting a dummy value for mock_api_key is not strictly needed here

        # Setup: Mocking the response with an error status code
        mock_response = AsyncMock(spec=ClientResponse)
        mock_response.status = 400
        mock_post.return_value.__aenter__.return_value = mock_response

        # Execution
        client = MistralClient(model_name="test_model", temperature=0.0)
        messages = [{"role": "user", "content": "hello"}]

        # Verification: Expecting a ValueError on error response
        with self.assertRaises(ValueError) as context:
            async for _ in await client.perform_stream_request(messages):  # type: ignore
                pass
        self.assertIn(
            "Server responded with an error. Status Code: 400", str(context.exception)
        )
