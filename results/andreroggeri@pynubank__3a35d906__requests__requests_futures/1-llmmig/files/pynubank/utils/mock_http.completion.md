### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the import of `Response` from `requests` with `Response` from `requests_futures.sessions`.
2. **Session Usage**: `requests_futures` provides asynchronous capabilities by using `FuturesSession`. However, since the provided code does not use asynchronous requests, the migration only involves ensuring compatibility with `requests_futures` by using `FuturesSession` for creating `Response` objects.
3. **Response Object**: Updated the `raw_get` and `raw_post` methods to use `FuturesSession` to create `Response` objects.

The rest of the code remains unchanged as it does not directly interact with the `requests` library in a way that requires asynchronous handling.

---

### Modified Code
```python
import fnmatch
import json
from pathlib import Path

from requests_futures.sessions import FuturesSession
from requests_futures.sessions import Response

from pynubank import NuException
from pynubank.utils.graphql import prepare_request_body
from pynubank.utils.http import HttpClient

GHOSTFLAME_URL = 'https://mocked-proxy-url/api/proxy/ghostflame_123'


class MockHttpClient(HttpClient):
    _results = {}

    def __init__(self):
        super().__init__()
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('account_balance')))] = self._read_data(
            'account_balance')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('account_feed')))] = self._read_data('account_feed')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('account_investments')))] = self._read_data(
            'account_investments')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('account_investments_yield')))] = self._read_data(
            'account_investments_yield')
        self._results[('https://*/api*bills/*', '')] = self._read_data('bills')
        self._results[('https://mocked-proxy-url/api/transactions/*', '')] = self._read_data('card_statement_detail')
        self._results[('https://mocked-proxy-url/api/proxy/bills_summary_123', '')] = self._read_data('bills_summary')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('account_id')))] = self._read_data('boleto_create')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('create_boleto')))] = self._read_data('boleto_create')
        self._results[('https://*/api/discovery', '')] = self._read_data('discovery_api')
        self._results[('https://*/api/app/discovery', '')] = self._read_data('discovery_app')
        self._results[('https://mocked-proxy-url/api/token', '')] = self._read_data('discovery_login')
        self._results[('https://mocked-proxy-url/api/proxy/login', '')] = self._read_data('discovery_login')
        self._results[('https://mocked-proxy-url/api/proxy/account_123', '')] = self._read_data('account')
        self._results[('https://mocked-proxy-url/api/proxy/lift', '')] = self._read_data('discovery_login')
        self._results[('https://mocked-proxy-url/api/proxy/events_123', '')] = self._read_data('proxy_events')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('create_money_request')))] = self._read_data('money')
        self._results[('https://mocked-proxy-url/api/proxy/customer_123', '')] = self._read_data('customer')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('get_pix_keys')))] = self._read_data('pix_keys')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('create_pix_money_request')))] = self._read_data(
            'pix_money_request')
        self._results[('https://mocked-proxy-url/api/proxy/revoke_token_123', '')] = {}

        self._results[(GHOSTFLAME_URL, str(prepare_request_body('create_pix_money_request')))] = self._read_data(
            'pix_money_request')
        self._results[GHOSTFLAME_URL, str(prepare_request_body('pix_receipt_screen'))] = self._read_data(
            'pix_receipt_screen')
        self._results[GHOSTFLAME_URL, str(prepare_request_body('account_feed_paginated'))] = self._read_data(
            'account_feed_paginated')
        self._results[(GHOSTFLAME_URL, str(prepare_request_body('account_savings')))] = self._read_data(
            'account_savings')

    def add_mock_url(self, url: str, graphql_object: str, response_json_name: str):
        self._results[(url, graphql_object)] = self._read_data(response_json_name)

    def remove_mock_url(self, route: tuple):
        del self._results[route]

    def get(self, url: str) -> dict:
        result = self._find(url)
        if result is None:
            raise NuException(f'There is no result expected for {url}')
        return result

    def post(self, url: str, json: dict) -> dict:
        result = self._find(url, json)
        if result is None:
            json['variables'] = {}
            result = self._find(url, json)

            if result is None:
                raise NuException(f'There is no result expected for {url}')
        return result

    def raw_get(self, url: str) -> Response:
        session = FuturesSession()
        res = session.get(url)
        res.result().status_code = 200
        return res.result()

    def raw_post(self, url: str, json: dict) -> Response:
        session = FuturesSession()
        res = session.post(url, json=json)
        res.result().status_code = 200
        return res.result()

    def _find(self, url: str, json: dict = None):
        result = self._results.get((url, ''))
        if result is not None:
            return result

        params = '' if json is None else str(json)
        for k in self._results.keys():
            if fnmatch.fnmatch(url, k[0]):
                return self._results.get((k[0], params))

    @staticmethod
    def _read_data(name):
        json_path = Path(__file__).parent.joinpath('mocked_responses', f'{name}.json').absolute()
        return json.loads(json_path.read_text())
```