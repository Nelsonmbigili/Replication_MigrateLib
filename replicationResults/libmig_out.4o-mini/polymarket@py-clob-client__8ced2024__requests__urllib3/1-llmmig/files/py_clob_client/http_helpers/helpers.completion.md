### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` library is a higher-level abstraction over HTTP requests, while `urllib3` is a lower-level library that requires more manual handling of requests and responses.

2. **Creating a PoolManager**: In `urllib3`, a `PoolManager` instance is created to manage connections. This is necessary to make requests.

3. **Making Requests**: The `requests.request()` method was replaced with the `PoolManager`'s `request()` method. The parameters passed to this method were adjusted to fit `urllib3`'s requirements.

4. **Handling Responses**: The response handling was modified to use `urllib3`'s response object. Instead of checking `status_code`, we check `status` and handle the response data accordingly.

5. **Error Handling**: The error handling was updated to catch exceptions specific to `urllib3`.

Here is the modified code:

```python
import urllib3
import json

from py_clob_client.clob_types import (
    DropNotificationParams,
    BalanceAllowanceParams,
    OrderScoringParams,
    OrdersScoringParams,
    TradeParams,
    OpenOrderParams,
)

from ..exceptions import PolyApiException

GET = "GET"
POST = "POST"
DELETE = "DELETE"
PUT = "PUT"

http = urllib3.PoolManager()

def overloadHeaders(method: str, headers: dict) -> dict:
    if headers is None:
        headers = dict()
    headers["User-Agent"] = "py_clob_client"

    headers["Accept"] = "*/*"
    headers["Connection"] = "keep-alive"
    headers["Content-Type"] = "application/json"

    if method == GET:
        headers["Accept-Encoding"] = "gzip"

    return headers


def request(endpoint: str, method: str, headers=None, data=None):
    try:
        headers = overloadHeaders(method, headers)
        resp = http.request(
            method=method, url=endpoint, headers=headers, body=json.dumps(data) if data else None
        )
        if resp.status != 200:
            raise PolyApiException(resp)

        try:
            return json.loads(resp.data)
        except json.JSONDecodeError:
            return resp.data.decode('utf-8')

    except urllib3.exceptions.HTTPError:
        raise PolyApiException(error_msg="Request exception!")


def post(endpoint, headers=None, data=None):
    return request(endpoint, POST, headers, data)


def get(endpoint, headers=None, data=None):
    return request(endpoint, GET, headers, data)


def delete(endpoint, headers=None, data=None):
    return request(endpoint, DELETE, headers, data)


def build_query_params(url: str, param: str, val: str) -> str:
    url_with_params = url
    last = url_with_params[-1]
    # if last character in url string == "?", append the param directly: api.com?param=value
    if last == "?":
        url_with_params = "{}{}={}".format(url_with_params, param, val)
    else:
        # else add "&", then append the param
        url_with_params = "{}&{}={}".format(url_with_params, param, val)
    return url_with_params


def add_query_trade_params(
    base_url: str, params: TradeParams = None, next_cursor="MA=="
) -> str:
    """
    Adds query parameters to a url
    """
    url = base_url
    if params:
        url = url + "?"
        if params.market:
            url = build_query_params(url, "market", params.market)
        if params.asset_id:
            url = build_query_params(url, "asset_id", params.asset_id)
        if params.after:
            url = build_query_params(url, "after", params.after)
        if params.before:
            url = build_query_params(url, "before", params.before)
        if params.maker_address:
            url = build_query_params(url, "maker_address", params.maker_address)
        if params.id:
            url = build_query_params(url, "id", params.id)
        if next_cursor:
            url = build_query_params(url, "next_cursor", next_cursor)
    return url


def add_query_open_orders_params(
    base_url: str, params: OpenOrderParams = None, next_cursor="MA=="
) -> str:
    """
    Adds query parameters to a url
    """
    url = base_url
    if params:
        url = url + "?"
        if params.market:
            url = build_query_params(url, "market", params.market)
        if params.asset_id:
            url = build_query_params(url, "asset_id", params.asset_id)
        if params.id:
            url = build_query_params(url, "id", params.id)
        if next_cursor:
            url = build_query_params(url, "next_cursor", next_cursor)
    return url


def drop_notifications_query_params(
    base_url: str, params: DropNotificationParams = None
) -> str:
    """
    Adds query parameters to a url
    """
    url = base_url
    if params:
        url = url + "?"
        if params.ids:
            url = build_query_params(url, "ids", ",".join(params.ids))
    return url


def add_balance_allowance_params_to_url(
    base_url: str, params: BalanceAllowanceParams = None
) -> str:
    """
    Adds query parameters to a url
    """
    url = base_url
    if params:
        url = url + "?"
        if params.asset_type:
            url = build_query_params(url, "asset_type", params.asset_type.__str__())
        if params.token_id:
            url = build_query_params(url, "token_id", params.token_id)
        if params.signature_type is not None:
            url = build_query_params(url, "signature_type", params.signature_type)
    return url


def add_order_scoring_params_to_url(
    base_url: str, params: OrderScoringParams = None
) -> str:
    """
    Adds query parameters to a url
    """
    url = base_url
    if params:
        url = url + "?"
        if params.orderId:
            url = build_query_params(url, "order_id", params.orderId)
    return url


def add_orders_scoring_params_to_url(
    base_url: str, params: OrdersScoringParams = None
) -> str:
    """
    Adds query parameters to a url
    """
    url = base_url
    if params:
        url = url + "?"
        if params.orderIds:
            url = build_query_params(url, "order_ids", ",".join(params.orderIds))
    return url
```