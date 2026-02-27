### Explanation of Changes:
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Library Import**: Replaced `import requests` with `import httpx`.
2. **HTTP Methods**: Updated all instances of `requests.get`, `requests.post`, and `requests.delete` to use `httpx.get`, `httpx.post`, and `httpx.delete` respectively.
3. **Parameter Handling**: The `httpx` library uses the same parameter structure as `requests`, so no changes were needed for `params` or `headers`.
4. **Response Handling**: The `.json()` method for parsing JSON responses remains the same in `httpx`, so no changes were needed there.
5. **Session Management**: Since the code does not use a persistent session, no changes were needed for session handling.

### Modified Code:
Below is the entire code with the necessary changes to use the `httpx` library instead of `requests`.

```python
import hashlib
import hmac
from datetime import datetime, timedelta
from enum import Enum

import httpx
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


class OrderStatus(Enum):
    NEW = 'NEW'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    REJECTED = 'REJECTED'


class OrderType(Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP = 'STOP'


class OrderSide(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class CandlesticksChartInervals(Enum):
    MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'
    THIRTY_MINUTES = '30m'
    HOUR = '1h'
    FOUR_HOURS = '4h'
    DAY = '1d'
    WEEK = '1w'


class TimeInForce(Enum):
    GTC = 'GTC'


class NewOrderResponseType(Enum):
    ACK = 'ACK'
    RESULT = 'RESULT'
    FULL = 'FULL'


class Client(object):
    """
    This is API for market Currency.com
    Please find documentation by https://exchange.currency.com/api
    Swagger UI: https://apitradedoc.currency.com/swagger-ui.html#/
    """

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = bytes(api_secret, 'utf-8')

    @staticmethod
    def _validate_limit(limit):
        max_limit = 1000
        valid_limits = [5, 10, 20, 50, 100, 500, 1000, 5000]
        if limit > max_limit:
            raise ValueError('Limit {} more than max limit: {}'.format(
                limit, max_limit
            ))
        if limit not in valid_limits:
            raise ValueError('Limit {} not among acceptable values: {}'.format(
                limit, valid_limits
            ))

    @staticmethod
    def _to_epoch_miliseconds(dttm: datetime):
        if dttm:
            return int(dttm.timestamp() * 1000)
        else:
            return dttm

    def _validate_recv_window(self, recv_window):
        max_value = CurrencyComConstants.RECV_WINDOW_MAX_LIMIT
        if recv_window and recv_window > max_value:
            raise ValueError(
                'recvValue cannot be greater than {}. Got {}.'.format(
                    max_value,
                    recv_window
                ))

    @staticmethod
    def _validate_new_order_resp_type(
            new_order_resp_type: NewOrderResponseType,
            order_type: OrderType
    ):
        if new_order_resp_type == NewOrderResponseType.ACK:
            raise ValueError('ACK mode no more available')

        if order_type == OrderType.MARKET:
            if new_order_resp_type not in [NewOrderResponseType.RESULT,
                                           NewOrderResponseType.FULL]:
                raise ValueError(
                    "new_order_resp_type for MARKET order can be only RESULT"
                    f"or FULL. Got {new_order_resp_type.value}")
        elif order_type == OrderType.LIMIT:
            if new_order_resp_type != NewOrderResponseType.RESULT:
                raise ValueError(
                    "new_order_resp_type for LIMIT order can be only RESULT."
                    f" Got {new_order_resp_type.value}")

    def _get_params_with_signature(self, **kwargs):
        t = self._to_epoch_miliseconds(datetime.now())
        kwargs['timestamp'] = t
        # pylint: disable=no-member
        body = RequestEncodingMixin._encode_params(kwargs)
        sign = hmac.new(self.api_secret, bytes(body, 'utf-8'),
                        hashlib.sha256).hexdigest()
        return {'signature': sign, **kwargs}

    def _get_header(self, **kwargs):
        return {
            **kwargs,
            CurrencyComConstants.HEADER_API_KEY_NAME: self.api_key
        }

    def _get(self, url, **kwargs):
        return httpx.get(url,
                         params=self._get_params_with_signature(**kwargs),
                         headers=self._get_header())

    def _post(self, url, **kwargs):
        return httpx.post(url,
                          params=self._get_params_with_signature(**kwargs),
                          headers=self._get_header())

    def _delete(self, url, **kwargs):
        return httpx.delete(url,
                            params=self._get_params_with_signature(
                                **kwargs),
                            headers=self._get_header())

    def get_account_info(self,
                         show_zero_balance: bool = False,
                         recv_window: int = None):
        self._validate_recv_window(recv_window)
        r = self._get(CurrencyComConstants.ACCOUNT_INFORMATION_ENDPOINT,
                      showZeroBalance=show_zero_balance,
                      recvWindow=recv_window)
        return r.json()

    def get_agg_trades(self, symbol,
                       start_time: datetime = None,
                       end_time: datetime = None,
                       limit=500):
        if limit > CurrencyComConstants.AGG_TRADES_MAX_LIMIT:
            raise ValueError('Limit should not exceed {}'.format(
                CurrencyComConstants.AGG_TRADES_MAX_LIMIT
            ))

        if start_time and end_time \
                and end_time - start_time > timedelta(hours=1):
            raise ValueError(
                'If both startTime and endTime are sent,'
                ' time between startTime and endTime must be less than 1 hour.'
            )

        params = {'symbol': symbol, 'limit': limit}

        if start_time:
            params['startTime'] = self._to_epoch_miliseconds(start_time)

        if end_time:
            params['endTime'] = self._to_epoch_miliseconds(end_time)

        r = httpx.get(CurrencyComConstants.AGGREGATE_TRADE_LIST_ENDPOINT,
                      params=params)

        return r.json()

    def close_trading_position(self, position_id, recv_window=None):
        self._validate_recv_window(recv_window)

        r = self._post(
            CurrencyComConstants.CLOSE_TRADING_POSITION_ENDPOINT,
            positionId=position_id,
            recvWindow=recv_window
        )
        return r.json()

    def get_order_book(self, symbol, limit=100):
        self._validate_limit(limit)
        r = httpx.get(CurrencyComConstants.ORDER_BOOK_ENDPOINT,
                      params={'symbol': symbol, 'limit': limit})
        return r.json()

    @staticmethod
    def get_exchange_info():
        r = httpx.get(CurrencyComConstants.EXCHANGE_INFORMATION_ENDPOINT)
        return r.json()

    def get_klines(self, symbol,
                   interval: CandlesticksChartInervals,
                   start_time: datetime = None,
                   end_time: datetime = None,
                   limit=500):
        if limit > CurrencyComConstants.KLINES_MAX_LIMIT:
            raise ValueError('Limit should not exceed {}'.format(
                CurrencyComConstants.KLINES_MAX_LIMIT
            ))

        params = {'symbol': symbol,
                  'interval': interval.value,
                  'limit': limit}

        if start_time:
            params['startTime'] = self._to_epoch_miliseconds(start_time)
        if end_time:
            params['endTime'] = self._to_epoch_miliseconds(end_time)
        r = httpx.get(CurrencyComConstants.KLINES_DATA_ENDPOINT,
                      params=params)
        return r.json()

    def get_leverage_settings(self, symbol, recv_window=None):
        self._validate_recv_window(recv_window)

        r = self._get(
            CurrencyComConstants.LEVERAGE_SETTINGS_ENDPOINT,
            symbol=symbol,
            recvWindow=recv_window
        )
        return r.json()

    def get_account_trade_list(self, symbol,
                               start_time: datetime = None,
                               end_time: datetime = None,
                               limit=500,
                               recv_window=None):
        self._validate_limit(limit)
        self._validate_recv_window(recv_window)

        params = {'symbol': symbol, 'limit': limit, 'recvWindow': recv_window}

        if start_time:
            params['startTime'] = self._to_epoch_miliseconds(start_time)

        if end_time:
            params['endTime'] = self._to_epoch_miliseconds(end_time)

        r = self._get(CurrencyComConstants.ACCOUNT_TRADE_LIST_ENDPOINT,
                      **params)

        return r.json()

    def get_open_orders(self, symbol=None, recv_window=None):
        self._validate_recv_window(recv_window)

        r = self._get(CurrencyComConstants.CURRENT_OPEN_ORDERS_ENDPOINT,
                      symbol=symbol,
                      recvWindow=recv_window)
        return r.json()

    def new_order(self,
                  symbol,
                  side: OrderSide,
                  order_type: OrderType,
                  quantity: float,
                  account_id: str = None,
                  expire_timestamp: datetime = None,
                  guaranteed_stop_loss: bool = False,
                  stop_loss: float = None,
                  take_profit: float = None,
                  leverage: int = None,
                  price: float = None,
                  new_order_resp_type: NewOrderResponseType
                  = NewOrderResponseType.FULL,
                  recv_window=None
                  ):
        self._validate_recv_window(recv_window)
        self._validate_new_order_resp_type(new_order_resp_type, order_type)

        if order_type == OrderType.LIMIT:
            if not price:
                raise ValueError('For LIMIT orders price is required or '
                                 f'should be greater than 0. Got {price}')

        expire_timestamp_epoch = self._to_epoch_miliseconds(expire_timestamp)

        r = self._post(
            CurrencyComConstants.ORDER_ENDPOINT,
            accountId=account_id,
            expireTimestamp=expire_timestamp_epoch,
            guaranteedStopLoss=guaranteed_stop_loss,
            leverage=leverage,
            newOrderRespType=new_order_resp_type.value,
            price=price,
            quantity=quantity,
            recvWindow=recv_window,
            side=side.value,
            stopLoss=stop_loss,
            symbol=symbol,
            takeProfit=take_profit,
            type=order_type.value,
        )
        return r.json()

    def cancel_order(self, symbol,
                     order_id,
                     recv_window=None):
        self._validate_recv_window(recv_window)

        r = self._delete(
            CurrencyComConstants.ORDER_ENDPOINT,
            symbol=symbol,
            orderId=order_id,
            recvWindow=recv_window
        )
        return r.json()

    @staticmethod
    def get_24h_price_change(symbol=None):
        r = httpx.get(CurrencyComConstants.PRICE_CHANGE_24H_ENDPOINT,
                      params={'symbol': symbol} if symbol else {})
        return r.json()

    @staticmethod
    def get_server_time():
        r = httpx.get(CurrencyComConstants.SERVER_TIME_ENDPOINT)

        return r.json()

    def list_leverage_trades(self, recv_window=None):
        self._validate_recv_window(recv_window)
        r = self._get(
            CurrencyComConstants.TRADING_POSITIONS_ENDPOINT,
            recvWindow=recv_window
        )
        return r.json()

    def update_trading_position(self,
                                position_id,
                                stop_loss: float = None,
                                take_profit: float = None,
                                guaranteed_stop_loss=False,
                                recv_window=None):
        self._validate_recv_window(recv_window)
        r = self._post(
            CurrencyComConstants.UPDATE_TRADING_POSITION_ENDPOINT,
            positionId=position_id,
            guaranteedStopLoss=guaranteed_stop_loss,
            stopLoss=stop_loss,
            takeProfit=take_profit
        )
        return r.json()
```

### Summary:
The migration from `requests` to `httpx` was straightforward as both libraries share similar APIs for basic HTTP operations. The changes were limited to replacing `requests` with `httpx` in the relevant parts of the code.