import pycurl
from io import BytesIO

# Replace all instances of requests.get with pycurl for GET requests
def _pycurl_get(url, headers, timeout):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.TIMEOUT, timeout)
    c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
    c.perform()
    c.close()
    return buffer.getvalue().decode('utf-8')

# Replace all instances of requests.post with pycurl for POST requests
def _pycurl_post(url, headers, timeout, payload):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.TIMEOUT, timeout)
    c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, payload)
    c.perform()
    c.close()
    return buffer.getvalue().decode('utf-8')

# Replace all instances of requests.put with pycurl for PUT requests
def _pycurl_put(url, headers, timeout, payload):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.TIMEOUT, timeout)
    c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
    c.setopt(c.CUSTOMREQUEST, "PUT")
    c.setopt(c.POSTFIELDS, payload)
    c.perform()
    c.close()
    return buffer.getvalue().decode('utf-8')

# Replace all instances of requests.delete with pycurl for DELETE requests
def _pycurl_delete(url, headers, timeout, payload=None):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.TIMEOUT, timeout)
    c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
    c.setopt(c.CUSTOMREQUEST, "DELETE")
    if payload:
        c.setopt(c.POSTFIELDS, payload)
    c.perform()
    c.close()
    return buffer.getvalue().decode('utf-8')

# Example of a modified function using pycurl for GET
def list_accounts(self, limit: int = 49, cursor: Optional[str] = None) -> AccountsPage:
    request_path = '/api/v3/brokerage/accounts'
    method = "GET"
    query_params = '?limit=' + str(limit)

    headers = self._build_request_headers(method, request_path) if self._is_legacy_auth(
    ) else self._build_request_headers_for_cloud(method, self._host, request_path)

    if cursor is not None:
        query_params = query_params + '&cursor=' + cursor

    response = _pycurl_get(self._base_url + request_path + query_params, headers, self.timeout)
    page = AccountsPage.from_response(response)
    return page

# Example of a modified function using pycurl for POST
def create_order(self, client_order_id: str, product_id: str, side: Side, order_configuration: dict, retail_portfolio_id: Optional[str] = None) -> Order:
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

    response = _pycurl_post(self._base_url + request_path, headers, self.timeout, json.dumps(payload))
    order = Order.from_create_order_response(response)
    return order

# Example of a modified function using pycurl for PUT
def edit_portfolio(self, portfolio_uuid: str, name: str) -> Portfolio:
    request_path = "/api/v3/brokerage/portfolios/" + portfolio_uuid
    method = "PUT"

    payload = {
        'name': name,
    }

    headers = self._build_request_headers(method, request_path, json.dumps(payload)) \
        if self._is_legacy_auth() \
        else self._build_request_headers_for_cloud(method, self._host, request_path)

    response = _pycurl_put(self._base_url + request_path, headers, self.timeout, json.dumps(payload))
    portfolio = Portfolio.from_response(response)
    return portfolio

# Example of a modified function using pycurl for DELETE
def delete_portfolio(self, portfolio_uuid: str) -> EmptyResponse:
    request_path = "/api/v3/brokerage/portfolios/" + portfolio_uuid
    method = "DELETE"

    payload = {}

    headers = self._build_request_headers(method, request_path, json.dumps(payload)) \
        if self._is_legacy_auth() \
        else self._build_request_headers_for_cloud(method, self._host, request_path)

    response = _pycurl_delete(self._base_url + request_path, headers, self.timeout, json.dumps(payload))
    return EmptyResponse.from_response(response)
