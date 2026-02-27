"""
Object models for products related endpoints args and response.
"""

from uuid import UUID
from datetime import datetime
from typing import List
from enum import Enum
import pycurl
import json
from io import BytesIO

from coinbaseadvanced.models.common import BaseModel
from coinbaseadvanced.models.error import CoinbaseAdvancedTradeAPIError


class ProductType(Enum):
    """
    Enum representing different product types.
    """

    SPOT = "SPOT"


GRANULARITY_MAP_IN_MINUTES = {
    "ONE_MINUTE": 1,
    "FIVE_MINUTE": 5,
    "FIFTEEN_MINUTE": 15,
    "THIRTY_MINUTE": 30,
    "ONE_HOUR": 60,
    "TWO_HOUR": 120,
    "SIX_HOUR": 360,
    "ONE_DAY": 1440,
}


class Granularity(Enum):
    """
    Enum representing time range for product candles.
    """

    UNKNOWN = "UNKNOWN_GRANULARITY"
    ONE_MINUTE = "ONE_MINUTE"
    FIVE_MINUTE = "FIVE_MINUTE"
    FIFTEEN_MINUTE = "FIFTEEN_MINUTE"
    THIRTY_MINUTE = "THIRTY_MINUTE"
    ONE_HOUR = "ONE_HOUR"
    TWO_HOUR = "TWO_HOUR"
    SIX_HOUR = "SIX_HOUR"
    ONE_DAY = "ONE_DAY"


def make_request_with_pycurl(url: str, method: str = "GET", headers: dict = None, data: dict = None):
    """
    Helper function to make HTTP requests using pycurl.
    """
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, buffer)

    if headers:
        curl.setopt(curl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

    if method == "POST" and data:
        curl.setopt(curl.POST, 1)
        curl.setopt(curl.POSTFIELDS, json.dumps(data))

    curl.perform()
    status_code = curl.getinfo(curl.RESPONSE_CODE)
    curl.close()

    response_body = buffer.getvalue().decode("utf-8")
    return response_body, status_code


class Product(BaseModel):
    """
    Object representing a product.
    """

    product_id: str
    price: str
    price_percentage_change_24h: str
    volume_24h: int
    volume_percentage_change_24h: str
    base_increment: str
    quote_increment: str
    quote_min_size: str
    quote_max_size: int
    base_min_size: str
    base_max_size: int
    base_name: str
    quote_name: str
    watched: bool
    is_disabled: bool
    new: bool
    status: str
    cancel_only: bool
    limit_only: bool
    post_only: bool
    trading_disabled: bool
    auction_mode: bool
    product_type: str
    quote_currency_id: str
    base_currency_id: str
    mid_market_price: str
    fcm_trading_session_details: str
    alias: str
    alias_to: list
    base_display_symbol: str
    quote_display_symbol: str

    def __init__(self,
                 product_id: str,
                 price: str,
                 price_percentage_change_24h: str,
                 volume_24h: int,
                 volume_percentage_change_24h: str,
                 base_increment: str,
                 quote_increment: str,
                 quote_min_size: str,
                 quote_max_size: int,
                 base_min_size: str,
                 base_max_size: int,
                 base_name: str,
                 quote_name: str,
                 watched: bool,
                 is_disabled: bool,
                 new: bool,
                 status: str,
                 cancel_only: bool,
                 limit_only: bool,
                 post_only: bool,
                 trading_disabled: bool,
                 auction_mode: bool,
                 product_type: str,
                 quote_currency_id: str,
                 base_currency_id: str,
                 mid_market_price: str,
                 fcm_trading_session_details: str,
                 alias: str,
                 alias_to: list,
                 base_display_symbol: str,
                 quote_display_symbol: str, **kwargs
                 ) -> None:
        self.product_id = product_id
        self.price = price
        self.price_percentage_change_24h = price_percentage_change_24h
        self.volume_24h = volume_24h
        self.volume_percentage_change_24h = volume_percentage_change_24h
        self.base_increment = base_increment
        self.quote_increment = quote_increment
        self.quote_min_size = quote_min_size
        self.quote_max_size = quote_max_size
        self.base_min_size = base_min_size
        self.base_max_size = base_max_size
        self.base_name = base_name
        self.quote_name = quote_name
        self.watched = watched
        self.is_disabled = is_disabled
        self.new = new
        self.status = status
        self.cancel_only = cancel_only
        self.limit_only = limit_only
        self.post_only = post_only
        self.trading_disabled = trading_disabled
        self.auction_mode = auction_mode
        self.product_type = product_type
        self.quote_currency_id = quote_currency_id
        self.base_currency_id = base_currency_id
        self.mid_market_price = mid_market_price
        self.fcm_trading_session_details = fcm_trading_session_details
        self.alias = alias
        self.alias_to = alias_to
        self.base_display_symbol = base_display_symbol
        self.quote_display_symbol = quote_display_symbol

        self.kwargs = kwargs

    @classmethod
    def from_response(cls, response: tuple) -> 'Product':
        """
        Factory Method.
        """

        response_body, status_code = response
        if status_code < 200 or status_code >= 300:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response_body)

        result = json.loads(response_body)
        product_dict = result
        return cls(**product_dict)


class ProductsPage(BaseModel):
    """
    Products Page.
    """

    products: List[Product]
    num_products: int

    def __init__(self, products: list, num_products: int, **kwargs) -> None:
        self.products = list(map(lambda x: Product(**x), products)) \
            if products is not None else []

        self.num_products = num_products

        self.kwargs = kwargs

    @classmethod
    def from_response(cls, response: tuple) -> 'ProductsPage':
        """
        Factory Method.
        """

        response_body, status_code = response
        if status_code < 200 or status_code >= 300:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response_body)

        result = json.loads(response_body)
        return cls(**result)

    def __iter__(self):
        return self.products.__iter__()
