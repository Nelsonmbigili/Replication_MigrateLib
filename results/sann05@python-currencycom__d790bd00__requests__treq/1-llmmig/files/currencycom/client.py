import hashlib
import hmac
from datetime import datetime, timedelta
from enum import Enum

import treq
from requests.models import RequestEncodingMixin


class CurrencyComConstants(object):
    HEADER_API_KEY_NAME = 'X-MBX-APIKEY'
    API_VERSION = 'v1'
    BASE_URL = 'https://api-adapter.backend.currency.com/api/{}/'.format(
        API_VERSION
    )

    AGG_TRADES_MAX_LIMIT = 1000
    KLINES_MAX_LIMIT = 1000
    RECV_WINDOW_MAX_LIMIT = 60000

    # Public API Endpoints
    SERVER_TIME_ENDPOINT = BASE_URL + 'time'
    EXCHANGE_INFORMATION_ENDPOINT = BASE_URL + 'exchangeInfo'

    # Market data Endpoints
    ORDER_BOOK_ENDPOINT = BASE_URL + 'depth'
    AGGREGATE_TRADE_LIST_ENDPOINT = BASE_URL + 'aggTrades'
    KLINES_DATA_ENDPOINT = BASE_URL + 'klines'
    PRICE_CHANGE_24H_ENDPOINT = BASE_URL + 'ticker/24hr'

    # Account Endpoints
    ACCOUNT_INFORMATION_ENDPOINT = BASE_URL + 'account'
    ACCOUNT_TRADE_LIST_ENDPOINT = BASE_URL + 'myTrades'

    # Order Endpoints
    ORDER_ENDPOINT = BASE_URL + 'order'
    CURRENT_OPEN_ORDERS_ENDPOINT = BASE_URL + 'openOrders'

    # Leverage Endpoints
    CLOSE_TRADING_POSITION_ENDPOINT = BASE_URL + 'closeTradingPosition'
    TRADING_POSITIONS_ENDPOINT = BASE_URL + 'tradingPositions'
    LEVERAGE_SETTINGS_ENDPOINT = BASE_URL + 'leverageSettings'
    UPDATE_TRADING_ORDERS_ENDPOINT = BASE_URL + 'updateTradingOrder'
    UPDATE_TRADING_POSITION_ENDPOINT = BASE_URL + 'updateTradingPosition'


class Client(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = bytes(api_secret, 'utf-8')

    @staticmethod
    def _to_epoch_miliseconds(dttm: datetime):
        if dttm:
            return int(dttm.timestamp() * 1000)
        else:
            return dttm

    def _get_params_with_signature(self, **kwargs):
        t = self._to_epoch_miliseconds(datetime.now())
        kwargs['timestamp'] = t
        body = RequestEncodingMixin._encode_params(kwargs)
        sign = hmac.new(self.api_secret, bytes(body, 'utf-8'),
                        hashlib.sha256).hexdigest()
        return {'signature': sign, **kwargs}

    def _get_header(self, **kwargs):
        return {
            **kwargs,
            CurrencyComConstants.HEADER_API_KEY_NAME: self.api_key
        }

    async def _get(self, url, **kwargs):
        response = await treq.get(
            url,
            params=self._get_params_with_signature(**kwargs),
            headers=self._get_header()
        )
        return await response.json()

    async def _post(self, url, **kwargs):
        response = await treq.post(
            url,
            params=self._get_params_with_signature(**kwargs),
            headers=self._get_header()
        )
        return await response.json()

    async def _delete(self, url, **kwargs):
        response = await treq.delete(
            url,
            params=self._get_params_with_signature(**kwargs),
            headers=self._get_header()
        )
        return await response.json()

    async def get_account_info(self, show_zero_balance: bool = False, recv_window: int = None):
        self._validate_recv_window(recv_window)
        return await self._get(
            CurrencyComConstants.ACCOUNT_INFORMATION_ENDPOINT,
            showZeroBalance=show_zero_balance,
            recvWindow=recv_window
        )

    async def get_agg_trades(self, symbol, start_time: datetime = None, end_time: datetime = None, limit=500):
        if limit > CurrencyComConstants.AGG_TRADES_MAX_LIMIT:
            raise ValueError('Limit should not exceed {}'.format(
                CurrencyComConstants.AGG_TRADES_MAX_LIMIT
            ))

        if start_time and end_time and end_time - start_time > timedelta(hours=1):
            raise ValueError(
                'If both startTime and endTime are sent,'
                ' time between startTime and endTime must be less than 1 hour.'
            )

        params = {'symbol': symbol, 'limit': limit}

        if start_time:
            params['startTime'] = self._to_epoch_miliseconds(start_time)

        if end_time:
            params['endTime'] = self._to_epoch_miliseconds(end_time)

        return await self._get(CurrencyComConstants.AGGREGATE_TRADE_LIST_ENDPOINT, **params)

    async def close_trading_position(self, position_id, recv_window=None):
        self._validate_recv_window(recv_window)
        return await self._post(
            CurrencyComConstants.CLOSE_TRADING_POSITION_ENDPOINT,
            positionId=position_id,
            recvWindow=recv_window
        )

    async def get_order_book(self, symbol, limit=100):
        self._validate_limit(limit)
        return await self._get(
            CurrencyComConstants.ORDER_BOOK_ENDPOINT,
            symbol=symbol,
            limit=limit
        )

    @staticmethod
    async def get_exchange_info():
        response = await treq.get(CurrencyComConstants.EXCHANGE_INFORMATION_ENDPOINT)
        return await response.json()

    async def get_klines(self, symbol, interval, start_time: datetime = None, end_time: datetime = None, limit=500):
        if limit > CurrencyComConstants.KLINES_MAX_LIMIT:
            raise ValueError('Limit should not exceed {}'.format(
                CurrencyComConstants.KLINES_MAX_LIMIT
            ))

        params = {'symbol': symbol, 'interval': interval.value, 'limit': limit}

        if start_time:
            params['startTime'] = self._to_epoch_miliseconds(start_time)
        if end_time:
            params['endTime'] = self._to_epoch_miliseconds(end_time)

        return await self._get(CurrencyComConstants.KLINES_DATA_ENDPOINT, **params)

    @staticmethod
    async def get_server_time():
        response = await treq.get(CurrencyComConstants.SERVER_TIME_ENDPOINT)
        return await response.json()
