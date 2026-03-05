### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Importing the FutureSession**: Instead of using `Session` from `requests.sessions`, we import `FuturesSession` from `requests_futures.sessions`.
2. **Creating an Instance of FuturesSession**: We replace the instantiation of `Session` with `FuturesSession`, which allows for asynchronous requests.
3. **No Changes to Request Logic**: The logic for making requests and handling parameters remains unchanged, as `requests_futures` is designed to be a drop-in replacement for `requests`.

Here is the modified code:

```python
# -*- coding: utf-8 -*-

import unittest.mock

from requests_futures.sessions import FuturesSession
from requests.auth import HTTPBasicAuth


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


@unittest.mock.patch('requests_futures.sessions.FuturesSession.request')
def test_camundarequest_session(mock, engine_url, MyRequest):
    request = MyRequest(url=engine_url)
    auth = HTTPBasicAuth(username='Jane', password='password')

    session = FuturesSession()
    session.auth = auth
    request.session = session

    request()

    assert mock.called
    assert request.session.auth.username == 'Jane'
    assert request.session.auth.password == 'password'
``` 

This code now uses `requests_futures` for handling requests asynchronously while maintaining the original structure and logic of the code.