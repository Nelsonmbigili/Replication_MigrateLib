from datetime import date, datetime
import logging
import asyncio
import time
import uuid
import jwt
import treq

from segment.analytics import utils
from segment.analytics.request import APIError
from segment.analytics.consumer import FatalError

class OauthManager(object):
    def __init__(self,
                 client_id,
                 client_key,
                 key_id,
                 auth_server='https://oauth2.segment.io',
                 scope='tracking_api:write',
                 timeout=15,
                 max_retries=3):
        self.client_id = client_id
        self.client_key = client_key
        self.key_id = key_id
        self.auth_server = auth_server
        self.scope = scope
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_count = 0
        self.clock_skew = 0
        
        self.log = logging.getLogger('segment')
        self.token_mutex = asyncio.Lock()
        self.token = None
        self.error = None
        self.poller_task = None

    async def get_token(self):
        async with self.token_mutex:
            if self.token:
                return self.token

        self.log.debug("OAuth is enabled. No cached access token.")
        
        # Start the poller loop if not already running
        if self.poller_task is None or self.poller_task.done():
            self.poller_task = asyncio.create_task(self._poller_loop())

        while True:
            # Wait for a token or error
            async with self.token_mutex:
                if self.token:
                    return self.token
                if self.error:
                    error = self.error
                    self.error = None
                    raise error
            await asyncio.sleep(1)

    async def clear_token(self):
        self.log.debug("OAuth Token invalidated. Poller for new token is {}".format(
            "active" if self.poller_task and not self.poller_task.done() else "stopped"))
        async with self.token_mutex:
            self.token = None

    async def _request_token(self):
        jwt_body = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": utils.remove_trailing_slash(self.auth_server),
            "iat": int(time.time()) - 5 - self.clock_skew,
            "exp": int(time.time()) + 55 - self.clock_skew,
            "jti": str(uuid.uuid4())
        }

        signed_jwt = jwt.encode(
            jwt_body,
            self.client_key,
            algorithm="RS256",
            headers={"kid": self.key_id},
        )

        request_body = 'grant_type=client_credentials&client_assertion_type='\
            'urn:ietf:params:oauth:client-assertion-type:jwt-bearer&'\
            'client_assertion={}&scope={}'.format(signed_jwt, self.scope)
        
        token_endpoint = f'{utils.remove_trailing_slash(self.auth_server)}/token'

        self.log.debug("OAuth token requested from {} with size {}".format(token_endpoint, len(request_body)))

        response = await treq.post(
            url=token_endpoint,
            data=request_body,
            timeout=self.timeout,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        return response

    async def _poller_loop(self):
        refresh_timer_ms = 25

        while True:
            response = None
            try:
                response = await self._request_token()
            except Exception as e:
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    self.log.debug("OAuth token request encountered an error on attempt {}: {}".format(self.retry_count, e))
                    await asyncio.sleep(refresh_timer_ms / 1000.0)
                    continue
                self.log.error("OAuth token request encountered an error after {} attempts: {}".format(self.retry_count, e))
                self.error = FatalError(str(e))
                return

            if response.headers.get("Date"):
                try:
                    server_time = datetime.strptime(response.headers.get("Date"), "%a, %d %b %Y %H:%M:%S %Z")
                    self.clock_skew = int((datetime.utcnow() - server_time).total_seconds())
                except Exception as e:
                    self.log.error("OAuth token request received a response with an invalid Date header: {} | {}".format(response, e))

            if response.code == 200:
                data = None
                try:
                    data = await response.json()
                except Exception as e:
                    self.retry_count += 1
                    if self.retry_count < self.max_retries:
                        await asyncio.sleep(refresh_timer_ms / 1000.0)
                        continue
                    self.error = e
                    return
                try:
                    async with self.token_mutex:
                        self.token = data['access_token']
                    self.retry_count = 0
                except Exception as e:
                    self.log.error("OAuth token request received a successful response with a missing token: {}".format(response))
                try:
                    refresh_timer_ms = int(data['expires_in']) / 2 * 1000
                except Exception as e:
                    refresh_timer_ms = 60 * 1000

            elif response.code == 429:
                self.retry_count += 1
                rate_limit_reset_time = None
                try:
                    rate_limit_reset_time = int(response.headers.get("X-RateLimit-Reset"))
                except Exception as e:
                    self.log.error("OAuth rate limit response did not have a valid rest time: {} | {}".format(response, e))
                if rate_limit_reset_time:
                    refresh_timer_ms = rate_limit_reset_time * 1000
                else:
                    refresh_timer_ms = 5 * 1000

                self.log.debug("OAuth token request encountered a rate limit response, waiting {} ms".format(refresh_timer_ms))
                await asyncio.sleep(refresh_timer_ms / 1000.0)
                refresh_timer_ms = 0
            elif response.code in [400, 401, 415]:
                self.retry_count = 0
                try:
                    payload = await response.json()

                    if (payload.get('error') == 'invalid_request' and
                        (payload.get('error_description') == 'Token is expired' or
                          payload.get('error_description') == 'Token used before issued')):
                        refresh_timer_ms = 0
                        continue
                    
                    self.error = APIError(response.code, payload['error'], payload['error_description'])
                except ValueError:
                    self.error = APIError(response.code, 'unknown', await response.text())
                self.log.error("OAuth token request error was unrecoverable, possibly due to configuration: {}".format(self.error))
                return
            else:
                self.log.debug("OAuth token request error, attempt {}: [{}] {}".format(self.retry_count, response.code, response.phrase))
                self.retry_count += 1

            if self.retry_count > 0 and self.retry_count % self.max_retries == 0:
                try:
                    payload = await response.json()
                    self.error = APIError(response.code, payload['error'], payload['error_description'])
                except ValueError:
                    self.error = APIError(response.code, 'unknown', await response.text())
                self.log.error("OAuth token request error after {} attempts: {}".format(self.retry_count, self.error))

            await asyncio.sleep(refresh_timer_ms / 1000.0)
