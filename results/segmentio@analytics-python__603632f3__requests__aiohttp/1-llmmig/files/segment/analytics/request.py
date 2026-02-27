from datetime import date, datetime
from io import BytesIO
from gzip import GzipFile
import logging
import json
from dateutil.tz import tzutc
import aiohttp
from aiohttp import ClientTimeout

from segment.analytics.version import VERSION
from segment.analytics.utils import remove_trailing_slash


async def post(write_key, host=None, gzip=False, timeout=15, proxies=None, oauth_manager=None, **kwargs):
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

    timeout_obj = ClientTimeout(total=timeout)
    res = None

    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        try:
            async with session.post(url, data=data, headers=headers) as response:
                res = response
                if res.status == 200:
                    log.debug('data uploaded successfully')
                    return res

                if oauth_manager and res.status in [400, 401, 403]:
                    oauth_manager.clear_token()

                try:
                    payload = await res.json()
                    log.debug('received response: %s', payload)
                    raise APIError(res.status, payload.get('code', 'unknown'), payload.get('message', 'unknown'))
                except aiohttp.ContentTypeError:
                    log.error('Unknown error: [%s] %s', res.status, res.reason)
                    raise APIError(res.status, 'unknown', await res.text())
        except aiohttp.ClientError as e:
            log.error(e)
            raise e


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
