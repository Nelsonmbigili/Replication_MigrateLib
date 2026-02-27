The following Python code currently uses the library "aiohttp" version 3.11.18.
Migrate this code to use the library "httpx" version 0.28.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "aiohttp" to "httpx".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "aiohttp" and "httpx".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import unittest
from unittest.mock import patch, MagicMock

from aiohttp import BasicAuth

from ingen.utils.app_http.http_request import HTTPRequest
from ingen.utils.app_http.aiohttp_retry import HTTPResponse
from ingen.utils.app_http.http_util import api_auth, execute_requests
from ingen.utils.app_http.success_criterias import get_criteria_by_name, DEFAULT_STATUS_CRITERIA_OPTIONS


class AsyncSessionMock(MagicMock):
    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass


class AsyncContextManagerMock(MagicMock):

    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass


def get_future_response(response_body):
    f = asyncio.Future()
    f.set_result(response_body)
    return f


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.auth = {'username': 'user', 'pwd': 'pwd', 'type': 'BasicAuth'}
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.request_params = {
            'retries': 2,
            'interval': 1,
            'interval_increment': 2,
            'success_criteria': get_criteria_by_name('status_criteria'),
            'criteria_options': DEFAULT_STATUS_CRITERIA_OPTIONS
        }

    def tearDown(self) -> None:
        self.loop.close()

    @patch('ingen.utils.app_http.http_util.Properties')
    def test_basic_auth(self, mock_properties):
        auth_config = {
            'type': 'BasicAuth',
            'username': 'username',
            'pwd': 'password'
        }
        mock_properties.get_property.return_value = 'username'
        auth = api_auth(auth_config)
        self.assertIsInstance(auth, BasicAuth)

    @patch('ingen.utils.app_http.http_util.http_retry_request')
    def test_single_request(self, mock_http_retry_request):
        requests = [HTTPRequest(url="www.test-url.com", method="GET")]
        response_body = {
            'name': 'Amit',
            'age': 32
        }
        empty_headers = dict()
        http_response = HTTPResponse(200, empty_headers, response_body)
        expected_response = [response_body]

        mock_http_retry_request.return_value = get_future_response(http_response)

        parsed_data = execute_requests(requests, self.request_params)
        self.assertListEqual(expected_response, parsed_data)

    @patch('ingen.utils.app_http.http_util.http_retry_request')
    def test_multiple_requests(self, mock_http_retry_request):
        requests = [
            HTTPRequest(url="www.test-url.com", method="GET"),
            HTTPRequest(url="www.test-url2.com", method="GET")
        ]
        response_json_1 = {
            'name': 'Amit',
            'age': '31'
        }
        response_json_2 = {
            'name': 'Kali',
            'age': '30'
        }
        http_response_1 = HTTPResponse(200, dict(), response_json_1)
        http_response_2 = HTTPResponse(200, dict(), response_json_2)

        expected_responses = [response_json_1, response_json_2]

        mock_http_retry_request.side_effect = [get_future_response(http_response_1),
                                               get_future_response(http_response_2)]

        parsed_data = execute_requests(requests, self.request_params)
        self.assertListEqual(expected_responses, parsed_data)


if __name__ == '__main__':
    unittest.main()

```