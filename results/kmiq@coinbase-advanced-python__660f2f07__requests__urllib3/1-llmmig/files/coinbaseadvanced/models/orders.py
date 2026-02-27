"""
Object models for order related endpoints args and response.
"""

from typing import List, Optional
from datetime import datetime
from enum import Enum

import urllib3

from coinbaseadvanced.models.common import BaseModel
from coinbaseadvanced.models.error import CoinbaseAdvancedTradeAPIError


class Side(Enum):
    """
    Enum representing whether "BUY" or "SELL" order.
    """

    BUY = "BUY"
    SELL = "SELL"


class StopDirection(Enum):
    """
    Enum direction in an stop order context.
    """

    UNKNOWN = "UNKNOWN_STOP_DIRECTION"
    UP = "STOP_DIRECTION_STOP_UP"
    DOWN = "STOP_DIRECTION_STOP_DOWN"


class OrderType(Enum):
    """
    Enum representing different order types.
    """

    UNKNOWN_ORDER_TYPE = "UNKNOWN_ORDER_TYPE"
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderPlacementSource(Enum):
    """
    Enum representing placements source for an order.
    """
    UNKNOWN = "UNKNOWN_PLACEMENT_SOURCE"
    RETAIL_ADVANCDED = "RETAIL_ADVANCED"


class OrderError(BaseModel):
    """
    Class encapsulating order error fields.
    """

    error: str
    message: str
    error_details: str
    preview_failure_reason: str
    new_order_failure_reason: str

    def __init__(self,
                 error: str = '',
                 message: str = '',
                 error_details: str = '',
                 preview_failure_reason: str = '',
                 new_order_failure_reason: str = '', **kwargs) -> None:
        self.error = error
        self.message = message
        self.error_details = error_details
        self.preview_failure_reason = preview_failure_reason
        self.new_order_failure_reason = new_order_failure_reason

        self.kwargs = kwargs


class LimitGTC(BaseModel):
    """
    Limit till cancelled order configuration.
    """

    base_size: str
    limit_price: str
    post_only: bool

    def __init__(self, base_size: str, limit_price: str, post_only: bool, **kwargs) -> None:
        self.base_size = base_size
        self.limit_price = limit_price
        self.post_only = post_only

        self.kwargs = kwargs


class LimitGTD(BaseModel):
    """
    Limit till date order configuration.
    """

    base_size: str
    limit_price: str
    post_only: bool
    end_time: datetime

    def __init__(self,
                 base_size: str,
                 limit_price: str,
                 post_only: bool,
                 end_time: str, **kwargs) -> None:
        self.base_size = base_size
        self.limit_price = limit_price
        self.post_only = post_only
        self.end_time = datetime.strptime(end_time if len(
            end_time) <= 27 else end_time[:26]+'Z', "%Y-%m-%dT%H:%M:%SZ")

        self.kwargs = kwargs


class MarketIOC(BaseModel):
    """
    Market order configuration.
    """

    quote_size: Optional[str]
    base_size: Optional[str]

    def __init__(self,
                 quote_size: Optional[str] = None,
                 base_size: Optional[str] = None, **kwargs) -> None:
        self.quote_size = quote_size
        self.base_size = base_size

        self.kwargs = kwargs


class StopLimitGTC(BaseModel):
    """
    Stop-Limit till cancelled order configuration.
    """

    base_size: str
    limit_price: str
    stop_price: str
    stop_direction: str

    def __init__(self,
                 base_size: str,
                 limit_price: str,
                 stop_price: str,
                 stop_direction: str, **kwargs) -> None:
        self.base_size = base_size
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.stop_direction = stop_direction

        self.kwargs = kwargs


class StopLimitGTD(BaseModel):
    """
    Stop-Limit till date order configuration.
    """

    base_size: float
    limit_price: str
    stop_price: str
    end_time: datetime
    stop_direction: str

    def __init__(self,
                 base_size: float,
                 limit_price: str,
                 stop_price: str,
                 end_time: str,
                 stop_direction: str, **kwargs) -> None:
        self.base_size = base_size
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.end_time = datetime.strptime(end_time if len(
            end_time) <= 27 else end_time[:26]+'Z', "%Y-%m-%dT%H:%M:%SZ")
        self.stop_direction = stop_direction

        self.kwargs = kwargs


class Order(BaseModel):
    """
    Class representing an order. This supports the `create_order*` endpoints
    and the `get_order` endpoint.
    """

    # (Fields omitted for brevity)

    @classmethod
    def from_create_order_response(cls, response: urllib3.response.HTTPResponse) -> 'Order':
        """
        Factory method from the `create_order` response object.
        """

        if response.status != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = json.loads(response.data.decode('utf-8'))

        if not result['success']:
            error_response = result['error_response']
            return cls(
                None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, error_response)

        success_response = result['success_response']
        order_configuration = result['order_configuration']
        return cls(**success_response, order_configuration=order_configuration)

    @classmethod
    def from_get_order_response(cls, response: urllib3.response.HTTPResponse) -> 'Order':
        """
        Factory method for creation from the `get_order` response object.
        """

        if response.status != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = json.loads(response.data.decode('utf-8'))

        order = result['order']

        return cls(**order)


class OrdersPage(BaseModel):
    """
    Orders page.
    """

    # (Fields omitted for brevity)

    @classmethod
    def from_response(cls, response: urllib3.response.HTTPResponse) -> 'OrdersPage':
        """
        Factory Method.
        """

        if response.status != 200:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response)

        result = json.loads(response.data.decode('utf-8'))
        return cls(**result)

    def __iter__(self):
        return self.orders.__iter__()
