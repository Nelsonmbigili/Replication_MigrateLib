### Explanation of Changes
The migration from the `requests` library to `urllib3` involves replacing `requests`-specific classes and methods with their `urllib3` equivalents. Here are the specific changes made:

1. **Session Replacement**: The `requests.Session` object is replaced with `urllib3.PoolManager`, which is the closest equivalent in `urllib3` for managing HTTP connections.
2. **Authentication**: `requests.auth.HTTPBasicAuth` is replaced with `urllib3.util.make_headers` to handle basic authentication headers.
3. **Mocking**: The `unittest.mock.patch` decorator is updated to mock `urllib3.PoolManager.request` instead of `requests.Session.request`.
4. **Request Execution**: The `Session.request` method is replaced with `PoolManager.request` for making HTTP requests.

### Modified Code
```python
# -*- coding: utf-8 -*-

import unittest.mock

from urllib3 import PoolManager
from urllib3.util import make_headers


def test_camundarequest_keeps_query_params(engine_url, MyRequest):

    assert MyRequest(url=engine_url, query_param='aStr').query_parameters()['param'] == 'aStr'
    assert MyRequest(url=engine_url, query_param=1).query_parameters()['param'] == 1


def test_camundarequest_keeps_body_params(engine_url, MyRequest):

    assert MyRequest(url=engine_url, body_param='aStr').body_parameters()['param'] == 'aStr'
    assert MyRequest(url=engine_url, body_param=1).body_parameters()['param'] == 1
    assert MyRequest(url=engine_url, body_param=True).body_parameters()['param'] is True
    assert MyRequest(url=engine_url, body_param=False).body_parameters()['param'] is False


def test_camundarequest_converts_bool_query_params(engine_url, MyRequest):

    assert MyRequest(url=engine_url, query_param=True).query_parameters()['param'] == 'true'
    assert MyRequest(url=engine_url, query_param=False).query_parameters()['param'] == 'false'


def test_camundarequest_converts_datetime_params(
    engine_url, MyRequest, date, date_tz, date_str, date_tz_str
):

    assert MyRequest(url=engine_url, query_param=date).query_parameters()['param'] == date_str
    assert MyRequest(url=engine_url, query_param=date_tz).query_parameters()['param'] == date_tz_str

    assert MyRequest(url=engine_url, body_param=date).body_parameters()['param'] == date_str
    assert MyRequest(url=engine_url, body_param=date_tz).body_parameters()['param'] == date_tz_str


@unittest.mock.patch('urllib3.PoolManager.request')
def test_camundarequest_session(mock, engine_url, MyRequest):
    request = MyRequest(url=engine_url)
    auth_headers = make_headers(basic_auth='Jane:password')

    pool_manager = PoolManager(headers=auth_headers)
    request.session = pool_manager

    request()

    assert mock.called
    assert request.session.headers['authorization'] == 'Basic SmFuZTpwYXNzd29yZA=='
```

### Key Points
- The `PoolManager` object is used to manage HTTP connections, replacing `Session`.
- Basic authentication is handled using `make_headers(basic_auth='username:password')`.
- The `unittest.mock.patch` decorator now mocks `urllib3.PoolManager.request` instead of `requests.Session.request`.
- The `authorization` header is checked directly in the `PoolManager` headers to verify authentication.