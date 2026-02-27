import hashlib
import hmac
from datetime import datetime, timedelta
from enum import Enum
import pycurl
from io import BytesIO
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

    def _make_request(self, method, url, params=None, headers=None):
        """
        Helper method to make HTTP requests using pycurl.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)

        if headers:
            curl.setopt(pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()])

        if method == 'GET' and params:
            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            curl.setopt(pycurl.URL, f"{url}?{query_string}")
        elif method == 'POST':
            curl.setopt(pycurl.POST, 1)
            if params:
                curl.setopt(pycurl.POSTFIELDS, '&'.join(f"{k}={v}" for k, v in params.items()))
        elif method == 'DELETE':
            curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
            if params:
                curl.setopt(pycurl.POSTFIELDS, '&'.join(f"{k}={v}" for k, v in params.items()))

        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.perform()
        curl.close()

        response = buffer.getvalue().decode('utf-8')
        return response

    def _get(self, url, **kwargs):
        return self._make_request('GET', url,
                                  params=self._get_params_with_signature(**kwargs),
                                  headers=self._get_header())

    def _post(self, url, **kwargs):
        return self._make_request('POST', url,
                                  params=self._get_params_with_signature(**kwargs),
                                  headers=self._get_header())

    def _delete(self, url, **kwargs):
        return self._make_request('DELETE', url,
                                  params=self._get_params_with_signature(**kwargs),
                                  headers=self._get_header())

    # The rest of the methods remain unchanged, but they now use `_get`, `_post`, and `_delete`.
