### Explanation of Changes:
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Nature**: `aiohttp` is an asynchronous library, so the `request` function and its dependent functions (`post`, `get`, `delete`) were converted to `async` functions.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` to make requests. A session is created and used within the `request` function.
3. **Request Execution**: The `aiohttp.ClientSession.request` method is used instead of `requests.request`.
4. **Response Handling**: The response is read using `await resp.json()` or `await resp.text()` since `aiohttp` operations are asynchronous.
5. **Error Handling**: `aiohttp` exceptions (`aiohttp.ClientError`) are handled instead of `requests.RequestException`.
6. **JSONDecodeError**: `aiohttp` does not have a `JSONDecodeError`. Instead, a `ContentTypeError` is raised when JSON decoding fails, so this is handled appropriately.

Below is the modified code:

---

### Modified Code:
```python
import aiohttp
import asyncio

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


async def request(endpoint: str, method: str, headers=None, data=None):
    try:
        headers = overloadHeaders(method, headers)
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method, url=endpoint, headers=headers, json=data if data else None
            ) as resp:
                if resp.status != 200:
                    raise PolyApiException(resp)

                try:
                    return await resp.json()
                except aiohttp.ContentTypeError:
                    return await resp.text()

    except aiohttp.ClientError:
        raise PolyApiException(error_msg="Request exception!")


async def post(endpoint, headers=None, data=None):
    return await request(endpoint, POST, headers, data)


async def get(endpoint, headers=None, data=None):
    return await request(endpoint, GET, headers, data)


async def delete(endpoint, headers=None, data=None):
    return await request(endpoint, DELETE, headers, data)


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

---

### Key Notes:
- The `request`, `post`, `get`, and `delete` functions are now `async`, so they must be called using `await` in an asynchronous context.
- The rest of the code remains unchanged as it does not directly interact with the HTTP library.