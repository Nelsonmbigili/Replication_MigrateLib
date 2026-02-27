"""
API Client for Coinbase Advanced Trade endpoints.
"""

import hmac
import hashlib
import time
import json
import treq  # Replaced requests with treq
import jwt

from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization

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

    async def list_accounts(self, limit: int = 49, cursor: Optional[str] = None) -> AccountsPage:
        """
        Get a list of authenticated accounts for the current user.
        """
        request_path = '/api/v3/brokerage/accounts'
        method = "GET"
        query_params = '?limit=' + str(limit)

        headers = self._build_request_headers(method, request_path) if self._is_legacy_auth(
        ) else self._build_request_headers_for_cloud(method, self._host, request_path)

        if cursor is not None:
            query_params = query_params + '&cursor=' + cursor

        response = await treq.get(self._base_url + request_path + query_params,
                                  headers=headers,
                                  timeout=self.timeout)
        response_json = await response.json()
        page = AccountsPage.from_response(response_json)
        return page

    async def get_account(self, account_id: str) -> Account:
        """
        Get a list of information about an account, given an account UUID.
        """
        request_path = f"/api/v3/brokerage/accounts/{account_id}"
        method = "GET"

        headers = self._build_request_headers(method, request_path) if self._is_legacy_auth(
        ) else self._build_request_headers_for_cloud(method, self._host, request_path)

        response = await treq.get(self._base_url + request_path,
                                  headers=headers,
                                  timeout=self.timeout)
        response_json = await response.json()
        account = Account.from_response(response_json)
        return account

    async def create_order(self, client_order_id: str,
                           product_id: str,
                           side: Side,
                           order_configuration: dict,
                           retail_portfolio_id: Optional[str] = None) -> Order:
        """
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

        response = await treq.post(self._base_url + request_path,
                                   json=payload,
                                   headers=headers,
                                   timeout=self.timeout)
        response_json = await response.json()
        order = Order.from_create_order_response(response_json)
        return order

    async def delete_portfolio(self, portfolio_uuid: str) -> EmptyResponse:
        """
        Delete a portfolio by portfolio ID.
        """
        request_path = "/api/v3/brokerage/portfolios/" + portfolio_uuid
        method = "DELETE"

        headers = self._build_request_headers(method, request_path) if self._is_legacy_auth(
        ) else self._build_request_headers_for_cloud(method, self._host, request_path)

        response = await treq.delete(self._base_url + request_path,
                                     headers=headers,
                                     timeout=self.timeout)
        response_json = await response.json()
        return EmptyResponse.from_response(response_json)

    # Helper Methods
    def _build_request_headers(self, method, request_path, body=''):
        timestamp = str(int(time.time()))
        message = timestamp + method + request_path + body
        signature = self._create_signature(message)

        return {
            "accept": "application/json",
            'CB-ACCESS-KEY': self._api_key,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-SIGN': signature,
        }

    def _create_signature(self, message):
        signature = hmac.new(
            self._secret_key.encode('utf-8'),
            message.encode('utf-8'),
            digestmod=hashlib.sha256).digest().hex()
        return signature

    def _is_legacy_auth(self) -> bool:
        return self._auth_schema == AuthSchema.LEGACY_API_KEYS
