### Explanation of Changes

To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statements**: The import statements for `requests` and `HTTPBasicAuth` were removed, and `treq` was imported instead.
2. **Session Handling**: The `Session` object from `requests` was replaced with `treq`'s built-in capabilities, as `treq` does not require a separate session object for making requests.
3. **Authentication**: The `HTTPBasicAuth` was removed since `treq` handles authentication differently. Instead, the authentication credentials were passed directly in the request call.
4. **Mocking**: The mock patching was updated to reflect the change in the request method from `requests` to `treq`.

Here is the modified code:

```python
# -*- coding: utf-8 -*-

import unittest.mock
import treq


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


@unittest.mock.patch('treq.request')
def test_camundarequest_session(mock, engine_url, MyRequest):
    request = MyRequest(url=engine_url)
    auth = ('Jane', 'password')

    request.auth = auth

    request()

    assert mock.called
    assert request.auth[0] == 'Jane'
    assert request.auth[1] == 'password'
``` 

This code now uses `treq` for making HTTP requests while maintaining the original structure and functionality of the tests.