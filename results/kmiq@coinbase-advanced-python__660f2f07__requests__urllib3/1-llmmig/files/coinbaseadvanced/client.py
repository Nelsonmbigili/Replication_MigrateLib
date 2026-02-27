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
import urllib3
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
    Enum representing authentication schema:
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
        self.http = urllib3.PoolManager()  # Initialize urllib3 PoolManager

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

        url = self._base_url + request_path + query_params
        response = self.http.request(
            "GET", url, headers=headers, timeout=self.timeout)

        if response.status != 200:
            raise Exception(f"Error: {response.status}, {response.data.decode('utf-8')}")

        page = AccountsPage.from_response(json.loads(response.data.decode('utf-8')))
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

        url = self._base_url + request_path
        response = self.http.request(
            "GET", url, headers=headers, timeout=self.timeout)

        if response.status != 200:
            raise Exception(f"Error: {response.status}, {response.data.decode('utf-8')}")

        account = Account.from_response(json.loads(response.data.decode('utf-8')))
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

        url = self._base_url + request_path
        response = self.http.request(
            "POST", url, body=json.dumps(payload), headers=headers, timeout=self.timeout)

        if response.status != 200:
            raise Exception(f"Error: {response.status}, {response.data.decode('utf-8')}")

        order = Order.from_create_order_response(json.loads(response.data.decode('utf-8')))
        return order

    # Additional methods (e.g., `list_orders`, `cancel_orders`, etc.) would follow the same pattern.
