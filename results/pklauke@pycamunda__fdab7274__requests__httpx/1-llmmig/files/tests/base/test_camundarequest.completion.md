### Explanation of Changes
To migrate the code from `requests` to `httpx`, the following changes were made:
1. **Import Changes**:
   - Replaced `requests.sessions.Session` with `httpx.Client` (as `httpx.Client` is the equivalent of `requests.Session`).
   - Replaced `requests.auth.HTTPBasicAuth` with `httpx.BasicAuth` (as `httpx.BasicAuth` is the equivalent of `requests.auth.HTTPBasicAuth`).

2. **Session Handling**:
   - Replaced `requests.Session` with `httpx.Client` for session management.
   - Updated the `auth` attribute of the session to use `httpx.BasicAuth`.

3. **Mocking**:
   - Updated the `unittest.mock.patch` decorator to patch `httpx.Client.request` instead of `requests.Session.request`.

These changes ensure the code uses `httpx` while maintaining the same functionality.

---

### Modified Code
```python
# -*- coding: utf-8 -*-

import unittest.mock

from httpx import Client, BasicAuth


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


@unittest.mock.patch('httpx.Client.request')
def test_camundarequest_session(mock, engine_url, MyRequest):
    request = MyRequest(url=engine_url)
    auth = BasicAuth(username='Jane', password='password')

    session = Client()
    session.auth = auth
    request.session = session

    request()

    assert mock.called
    assert request.session.auth.username == 'Jane'
    assert request.session.auth.password == 'password'
```

---

### Key Points
- The migration was limited to replacing `requests` with `httpx` equivalents.
- The `httpx.Client` and `httpx.BasicAuth` were used to replace `requests.Session` and `requests.auth.HTTPBasicAuth`, respectively.
- Mocking was updated to patch `httpx.Client.request` instead of `requests.Session.request`.