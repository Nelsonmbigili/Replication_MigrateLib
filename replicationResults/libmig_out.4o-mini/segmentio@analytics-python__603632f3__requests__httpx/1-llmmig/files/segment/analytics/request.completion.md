### Explanation of Changes

To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: The import for `requests` was replaced with `httpx`.
2. **Session Handling**: The `requests` session was replaced with `httpx`'s client. Instead of using `_session.post(...)`, we will use `httpx.Client().post(...)`.
3. **Response Handling**: The way to access the response content and status code remains similar, but we will use `res.status_code` and `res.json()` directly from the `httpx` response object.
4. **Timeout Handling**: The timeout parameter is passed directly to the `post` method in `httpx`.

Here is the modified code:

```python
from datetime import date, datetime
from io import BytesIO
from gzip import GzipFile
import logging
import json
from dateutil.tz import tzutc
from httpx import Client

from segment.analytics.version import VERSION
from segment.analytics.utils import remove_trailing_slash

_client = Client()

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
            gz.write(data.encode('utf-8'))
        data = buf.getvalue()

    kwargs = {
        "data": data,
        "headers": headers,
        "timeout": timeout,
    }

    if proxies:
        kwargs['proxies'] = proxies
    res = None
    try:
        res = _client.post(url, **kwargs)
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
        log.error('Unknown error: [%s] %s', res.status_code, res.text)
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

This code now uses `httpx` for making HTTP requests while maintaining the original structure and functionality of the code.