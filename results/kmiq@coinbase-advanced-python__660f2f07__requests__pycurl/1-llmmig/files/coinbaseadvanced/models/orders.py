"""
Object models for order related endpoints args and response.
"""

from typing import List, Optional
from datetime import datetime
from enum import Enum
import pycurl
import json
from io import BytesIO

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


# Other classes remain unchanged...

class Order(BaseModel):
    """
    Class representing an order. This supports the `create_order*` endpoints
    and the `get_order` endpoint.
    """

    # Fields remain unchanged...

    def __init__(self,
                 order_id: Optional[str],
                 product_id: Optional[str],
                 side: Optional[str],
                 client_order_id: Optional[str],
                 order_configuration: Optional[dict],
                 user_id: Optional[str] = None,
                 status: Optional[str] = None,
                 time_in_force: Optional[str] = None,
                 created_time: Optional[str] = None,
                 completion_percentage: Optional[int] = None,
                 filled_size: Optional[str] = None,
                 average_filled_price: Optional[int] = None,
                 fee: Optional[str] = None,
                 number_of_fills: Optional[int] = None,
                 filled_value: Optional[int] = None,
                 pending_cancel: Optional[bool] = None,
                 size_in_quote: Optional[bool] = None,
                 total_fees: Optional[str] = None,
                 size_inclusive_of_fees: Optional[bool] = None,
                 total_value_after_fees: Optional[str] = None,
                 trigger_status: Optional[str] = None,
                 order_type: Optional[str] = None,
                 reject_reason: Optional[str] = None,
                 settled: Optional[str] = None,
                 product_type: Optional[str] = None,
                 reject_message: Optional[str] = None,
                 cancel_message: Optional[str] = None,
                 order_placement_source: Optional[str] = None,
                 outstanding_hold_amount: Optional[str] = None,

                 is_liquidation: Optional[bool] = None,
                 last_fill_time: Optional[str] = None,
                 edit_history: Optional[List[OrderEditRecord]] = None,
                 leverage: Optional[str] = None,
                 margin_type: Optional[str] = None,

                 order_error: Optional[dict] = None, **kwargs) -> None:
        # Initialization remains unchanged...

    @classmethod
    def from_create_order_response(cls, url: str, headers: dict, data: dict) -> 'Order':
        """
        Factory method from the `create_order` response object using pycurl.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
        curl.setopt(pycurl.POSTFIELDS, json.dumps(data))
        curl.setopt(pycurl.WRITEDATA, buffer)

        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()

        if status_code != 200:
            raise CoinbaseAdvancedTradeAPIError(f"HTTP Error: {status_code}")

        response_body = buffer.getvalue().decode('utf-8')
        result = json.loads(response_body)

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
    def from_get_order_response(cls, url: str, headers: dict) -> 'Order':
        """
        Factory method for creation from the `get_order` response object using pycurl.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
        curl.setopt(pycurl.WRITEDATA, buffer)

        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()

        if status_code != 200:
            raise CoinbaseAdvancedTradeAPIError(f"HTTP Error: {status_code}")

        response_body = buffer.getvalue().decode('utf-8')
        result = json.loads(response_body)

        order = result['order']
        return cls(**order)


class OrdersPage(BaseModel):
    """
    Orders page.
    """

    # Fields remain unchanged...

    @classmethod
    def from_response(cls, url: str, headers: dict) -> 'OrdersPage':
        """
        Factory Method using pycurl.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
        curl.setopt(pycurl.WRITEDATA, buffer)

        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()

        if status_code != 200:
            raise CoinbaseAdvancedTradeAPIError(f"HTTP Error: {status_code}")

        response_body = buffer.getvalue().decode('utf-8')
        result = json.loads(response_body)
        return cls(**result)

    def __iter__(self):
        return self.orders.__iter__()
