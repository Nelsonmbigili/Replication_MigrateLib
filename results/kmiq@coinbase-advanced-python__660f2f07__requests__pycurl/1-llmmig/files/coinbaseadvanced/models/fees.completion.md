### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.Response` with `pycurl` for HTTP requests**:
   - The `from_response` method was updated to use `pycurl` for making HTTP requests instead of `requests`.
   - `pycurl` does not have a direct equivalent to `requests.Response`. Instead, we use a `BytesIO` object to capture the response body and handle HTTP status codes manually.
2. **Error Handling**:
   - `pycurl` does not provide a built-in `ok` attribute like `requests.Response`. Instead, we manually check the HTTP status code returned by `pycurl`.
3. **JSON Parsing**:
   - The response body captured by `pycurl` is in bytes, so it is decoded to a string and then parsed as JSON using the `json` module.

Below is the modified code:

---

### Modified Code:
```python
"""
Object models for fees related endpoints args and response.
"""

from typing import Optional
import pycurl
from io import BytesIO
import json

from coinbaseadvanced.models.common import BaseModel
from coinbaseadvanced.models.error import CoinbaseAdvancedTradeAPIError


class FeeTier(BaseModel):
    """
    Fee Tier object.
    """

    pricing_tier: str
    usd_from: int
    usd_to: str
    taker_fee_rate: str
    maker_fee_rate: str

    def __init__(self,
                 pricing_tier: str,
                 usd_from: int,
                 usd_to: str,
                 taker_fee_rate: str,
                 maker_fee_rate: str, **kwargs) -> None:
        self.pricing_tier = pricing_tier
        self.usd_from = usd_from
        self.usd_to = usd_to
        self.taker_fee_rate = taker_fee_rate
        self.maker_fee_rate = maker_fee_rate

        self.kwargs = kwargs


class GoodsAndServicesTax(BaseModel):
    """
    Object representing Goods and Services Tax data.
    """

    rate: str
    type: str

    def __init__(self, rate: str, type: str, **kwargs) -> None:
        self.rate = rate
        self.type = type

        self.kwargs = kwargs


class MarginRate(BaseModel):
    """
    Margin Rate.
    """

    value: str

    def __init__(self, value: str, **kwargs) -> None:
        self.value = value

        self.kwargs = kwargs


class TransactionsSummary(BaseModel):
    """
    Transactions Summary.
    """

    total_volume: int
    total_fees: int
    fee_tier: Optional[FeeTier]
    margin_rate: Optional[MarginRate]
    goods_and_services_tax: Optional[GoodsAndServicesTax]
    advanced_trade_only_volume: int
    advanced_trade_only_fees: int
    coinbase_pro_volume: int
    coinbase_pro_fees: int
    total_balance: str
    has_promo_fee: bool

    def __init__(self,
                 total_volume: int,
                 total_fees: int,
                 fee_tier: dict,
                 margin_rate: dict,
                 goods_and_services_tax: dict,
                 advanced_trade_only_volume: int,
                 advanced_trade_only_fees: int,
                 coinbase_pro_volume: int,
                 coinbase_pro_fees: int,
                 total_balance: str,
                 has_promo_fee: bool, **kwargs) -> None:
        self.total_volume = total_volume
        self.total_fees = total_fees
        self.fee_tier = FeeTier(**fee_tier) if fee_tier is not None else None
        self.margin_rate = MarginRate(
            **margin_rate) if margin_rate is not None else None
        self.goods_and_services_tax = GoodsAndServicesTax(
            **goods_and_services_tax) if goods_and_services_tax is not None else None
        self.advanced_trade_only_volume = advanced_trade_only_volume
        self.advanced_trade_only_fees = advanced_trade_only_fees
        self.coinbase_pro_volume = coinbase_pro_volume
        self.coinbase_pro_fees = coinbase_pro_fees

        self.total_balance = total_balance
        self.has_promo_fee = has_promo_fee

        self.kwargs = kwargs

    @classmethod
    def from_response(cls, url: str) -> 'TransactionsSummary':
        """
        Factory Method.
        """

        buffer = BytesIO()
        curl = pycurl.Curl()

        try:
            # Set up the pycurl request
            curl.setopt(curl.URL, url)
            curl.setopt(curl.WRITEFUNCTION, buffer.write)
            curl.setopt(curl.FOLLOWLOCATION, True)
            curl.setopt(curl.TIMEOUT, 30)

            # Perform the request
            curl.perform()

            # Get the HTTP response code
            status_code = curl.getinfo(curl.RESPONSE_CODE)

            # Check if the response is not OK
            if status_code < 200 or status_code >= 300:
                raise CoinbaseAdvancedTradeAPIError(
                    f"HTTP Error: {status_code} for URL: {url}"
                )

            # Parse the response body
            response_body = buffer.getvalue().decode('utf-8')
            result = json.loads(response_body)

            return cls(**result)

        except pycurl.error as e:
            raise CoinbaseAdvancedTradeAPIError(f"Request failed: {e}")

        finally:
            # Clean up
            curl.close()
            buffer.close()
```

---

### Key Points:
1. The `from_response` method now accepts a `url` string instead of a `requests.Response` object.
2. `pycurl` is used to perform the HTTP request, and the response is captured in a `BytesIO` buffer.
3. The HTTP status code is manually checked to determine if the request was successful.
4. The response body is decoded and parsed as JSON using the `json` module.
5. Proper error handling is implemented for both HTTP errors and `pycurl` exceptions.