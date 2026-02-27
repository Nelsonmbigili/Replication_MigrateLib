### Explanation of Changes:
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:
1. **Library Import**: Replaced the `requests` import with `requests_futures`.
2. **Asynchronous Requests**: Updated the `requests.get`, `requests.post`, `requests.put`, and `requests.delete` calls to use the `requests_futures.sessions.FuturesSession` object for asynchronous requests.
3. **Session Initialization**: Added a `FuturesSession` instance (`self.session`) in the `CoinbaseAdvancedTradeAPIClient` class to handle all HTTP requests.
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual response synchronously where needed.

### Modified Code:
Below is the updated code with the migration to `requests_futures`:

```python
"""
API Client for Coinbase Advanced Trade endpoints.
"""

import hmac
import hashlib
import time
import json

from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from requests_futures.sessions import FuturesSession
import jwt

from coinbaseadvanced.models.common import EmptyResponse, UnixTime
from coinbaseadvanced.models.fees import TransactionsSummary
from coinbaseadvanced.models.portfolios import Portfolio, PortfolioBreakdown, \
    PortfolioFundsTransfer, PortfolioType, PortfoliosPage
from coinbaseadvanced.models.products import BidAsksPage, ProductBook, ProductsPage, Product, \
    CandlesPage, TradesPage, ProductType, Granularity, GRANULARITY_MAP_IN_MINUTES
from coinbaseadvanced.models.accounts import AccountsPage, Account
from coinbaseadvanced.models.orders import OrderEditPreview, OrderPlacementSource, OrdersPage, Order, OrderEdit, \
    OrderBatchCancellation, FillsPage, Side, StopDirection, OrderType


class AuthSchema(Enum):
    """
    Enum representing authetication schema:
    https://docs.cdp.coinbase.com/advanced-trade/docs/auth#authentication-schemes
    """

    CLOUD_API_TRADING_KEYS = "CLOUD_API_TRADING_KEYS"
    LEGACY_API_KEYS = "LEGACY_API_KEYS"


class CoinbaseAdvancedTradeAPIClient(object):
    """
    API Client for Coinbase Advanced Trade endpoints.
    """

    def __init__(self,
                 api_key: str,
                 secret_key: str,
                 base_url: str = 'https://api.coinbase.com',
                 timeout: int = 10,
                 auth_schema: AuthSchema = AuthSchema.LEGACY_API_KEYS
                 ) -> None:
        self._base_url = base_url
        self._host = base_url[8:]
        self._api_key = api_key
        self._secret_key = secret_key
        self.timeout = timeout
        self._auth_schema = auth_schema
        self.session = FuturesSession()  # Initialize FuturesSession for async requests

    @staticmethod
    def from_legacy_api_keys(api_key: str,
                             secret_key: str):
        """
        Factory method for legacy auth schema.
        API keys for this schema are generated via: https://www.coinbase.com/settings/api
        """
        return CoinbaseAdvancedTradeAPIClient(api_key=api_key, secret_key=secret_key)

    @staticmethod
    def from_cloud_api_keys(api_key_name: str,
                            private_key: str):
        """
        Factory method for cloud auth schema (recommended by Coinbase).
        API keys for this schema are generated via: https://cloud.coinbase.com/access/api
        """
        return CoinbaseAdvancedTradeAPIClient(api_key=api_key_name, secret_key=private_key,
                                              auth_schema=AuthSchema.CLOUD_API_TRADING_KEYS)

    # Accounts #

    def list_accounts(self, limit: int = 49, cursor: Optional[str] = None) -> AccountsPage:
        """
        https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_getaccounts/

        Get a list of authenticated accounts for the current user.
        """
        request_path = '/api/v3/brokerage/accounts'
        method = "GET"
        query_params = '?limit=' + str(limit)

        headers = self._build_request_headers(method, request_path) if self._is_legacy_auth(
        ) else self._build_request_headers_for_cloud(method, self._host, request_path)

        if cursor is not None:
            query_params = query_params + '&cursor=' + cursor

        # Use FuturesSession for the GET request
        future_response = self.session.get(self._base_url + request_path + query_params,
                                           headers=headers,
                                           timeout=self.timeout)
        response = future_response.result()  # Wait for the response synchronously
        page = AccountsPage.from_response(response)
        return page

    def get_account(self, account_id: str) -> Account:
        """
        https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_getaccount

        Get a list of information about an account, given an account UUID.
        """
        request_path = f"/api/v3/brokerage/accounts/{account_id}"
        method = "GET"

        headers = self._build_request_headers(method, request_path) if self._is_legacy_auth(
        ) else self._build_request_headers_for_cloud(method, self._host, request_path)

        # Use FuturesSession for the GET request
        future_response = self.session.get(self._base_url + request_path,
                                           headers=headers,
                                           timeout=self.timeout)
        response = future_response.result()  # Wait for the response synchronously
        account = Account.from_response(response)
        return account

    def create_order(self, client_order_id: str,
                     product_id: str,
                     side: Side,
                     order_configuration: dict,
                     retail_portfolio_id: Optional[str] = None) -> Order:
        """
        https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_postorder

        Create an order with a specified product_id (asset-pair), side (buy/sell), etc.
        """
        request_path = "/api/v3/brokerage/orders"
        method = "POST"

        payload = {
            'client_order_id': client_order_id,
            'product_id': product_id,
            'side': side.value,
            'order_configuration': order_configuration,
        }
        if retail_portfolio_id is not None:
            payload['retail_portfolio_id'] = retail_portfolio_id

        headers = self._build_request_headers(method, request_path, json.dumps(payload)) \
            if self._is_legacy_auth() \
            else self._build_request_headers_for_cloud(method, self._host, request_path)

        # Use FuturesSession for the POST request
        future_response = self.session.post(self._base_url + request_path,
                                            json=payload, headers=headers,
                                            timeout=self.timeout)
        response = future_response.result()  # Wait for the response synchronously
        order = Order.from_create_order_response(response)
        return order

    def delete_portfolio(self, portfolio_uuid: str) -> EmptyResponse:
        """
        https://docs.cdp.coinbase.com/advanced-trade/reference/retailbrokerageapi_deleteportfolio

        Delete a portfolio by portfolio ID.
        """
        request_path = "/api/v3/brokerage/portfolios/" + portfolio_uuid
        method = "DELETE"

        payload = {}

        headers = self._build_request_headers(method, request_path, json.dumps(payload)) \
            if self._is_legacy_auth(
        ) else self._build_request_headers_for_cloud(method, self._host, request_path)

        # Use FuturesSession for the DELETE request
        future_response = self.session.delete(self._base_url + request_path,
                                              json=payload, headers=headers,
                                              timeout=self.timeout)
        response = future_response.result()  # Wait for the response synchronously
        return EmptyResponse.from_response(response)

    # Other methods follow the same pattern: replacing `requests` with `self.session` and using `.result()` to retrieve the response.
```

### Key Notes:
- The `FuturesSession` object is used for all HTTP requests (`GET`, `POST`, `PUT`, `DELETE`).
- The `.result()` method ensures that the response is retrieved synchronously, maintaining the original behavior of the code.
- Only the HTTP request logic was updated; no other parts of the code were modified.