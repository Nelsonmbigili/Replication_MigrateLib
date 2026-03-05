### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The import statement for `requests` was replaced with `requests_futures.sessions`. This allows us to use the `FuturesSession` class, which supports asynchronous requests.
2. **Session Initialization**: The `_session` variable was changed from a `requests.Session()` to `FuturesSession()`, which is part of the `requests_futures` library.
3. **Asynchronous Request**: The `post` method of the session was changed to `session.post()` to utilize the asynchronous capabilities of `requests_futures`. The response handling was adjusted to wait for the future to complete.

Here is the modified code:

```python
from datetime import date, datetime
from io import BytesIO
from gzip import GzipFile
import logging
import json
from dateutil.tz import tzutc
from requests.auth import HTTPBasicAuth
from requests_futures.sessions import FuturesSession  # Changed import

from segment.analytics.version import VERSION
from segment.analytics.utils import remove_trailing_slash

_session = FuturesSession()  # Changed to FuturesSession


def post(write_key, host=None, gzip=False, timeout=15, proxies=None, oauth_manager=None, **kwargs):
    """Post the `kwargs` to the API"""
    log = logging.getLogger('segment')
    body = kwargs
    if not "sentAt" in body.keys():
        body["sentAt"] = datetime.now(tz=tzutc()).isoformat()
    body["writeKey"] = write_key
    url = remove_trailing_slash(host or 'https://api.segment.io') + '/v1/batch'
    auth = None
    if oauth_manager:
        auth = oauth_manager.get_token()
    data = json.dumps(body, cls=DatetimeSerializer)
    log.debug('making request: %s', data)
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'analytics-python/' + VERSION
    }
    if auth:
        headers['Authorization'] = 'Bearer {}'.format(auth)

    if gzip:
        headers['Content-Encoding'] = 'gzip'
        buf = BytesIO()
        with GzipFile(fileobj=buf, mode='w') as gz:
            # 'data' was produced by json.dumps(),
            # whose default encoding is utf-8.
            gz.write(data.encode('utf-8'))
        data = buf.getvalue()

    kwargs = {
        "data": data,
        "headers": headers,
        "timeout": 15,
    }

    if proxies:
        kwargs['proxies'] = proxies
    res = None
    try:
        future = _session.post(url, data=data, headers=headers, timeout=timeout)  # Changed to use future
        res = future.result()  # Wait for the future to complete
    except Exception as e:
        log.error(e)
        raise e
        
    if res.status_code == 200:
        log.debug('data uploaded successfully')
        return res

    if oauth_manager and res.status_code in [400, 401, 403]:
        oauth_manager.clear_token()

    try:
        payload = res.json()
        log.debug('received response: %s', payload)
        raise APIError(res.status_code, payload['code'], payload['message'])
    except ValueError:
        log.error('Unknown error: [%s] %s', res.status_code, res.reason)
        raise APIError(res.status_code, 'unknown', res.text)


class APIError(Exception):

    def __init__(self, status, code, message):
        self.message = message
        self.status = status
        self.code = code

    def __str__(self):
        msg = "[Segment] {0}: {1} ({2})"
        return msg.format(self.code, self.message, self.status)


class DatetimeSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
``` 

This code now uses `requests_futures` to handle asynchronous HTTP requests while maintaining the original structure and functionality.