### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Importing `requests_futures`**: The `requests` library was replaced with `requests_futures` in the imports. Specifically, `from requests_futures.sessions import FuturesSession` was added, and the `requests` module was replaced with `FuturesSession` where applicable.
2. **Session Initialization**: A `FuturesSession` object was created and used for all HTTP requests instead of directly using `requests`.
3. **Asynchronous Requests**: The `requests_futures` library allows for asynchronous requests. However, since the original code does not use asynchronous behavior, the `.result()` method was called on the returned future objects to maintain synchronous behavior.
4. **Replaced `requests.request` and Other Methods**: All instances of `requests.request`, `requests.get`, `requests.post`, etc., were replaced with the corresponding methods of the `FuturesSession` object.

### Modified Code:
```python
# Copyright (c) 2024 Dell Inc. or its subsidiaries.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from requests_futures.sessions import FuturesSession
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from PyPowerFlex import exceptions
from PyPowerFlex import utils

# Disable insecure request warnings
FuturesSession().session.verify = False
LOG = logging.getLogger(__name__)


class Request:
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"

    def __init__(self, token, configuration):
        self.token = token
        self.configuration = configuration
        self.__refresh_token = None
        self.session = FuturesSession()  # Initialize FuturesSession

    @property
    def base_url(self):
        return 'https://{address}:{port}/api'.format(
            address=self.configuration.gateway_address,
            port=self.configuration.gateway_port
        )

    @property
    def auth_url(self):
        return 'https://{address}:{port}/rest/auth'.format(
            address=self.configuration.gateway_address,
            port=self.configuration.gateway_port
        )

    @property
    def headers(self):
        return {'content-type': 'application/json'}

    @property
    def verify_certificate(self):
        verify_certificate = self.configuration.verify_certificate
        if (
                self.configuration.verify_certificate
                and self.configuration.certificate_path
        ):
            verify_certificate = self.configuration.certificate_path
        return verify_certificate

    def get_auth_headers(self, request_type=None):
        if request_type == self.GET:
            return {'Authorization': 'Bearer {0}'.format(self.token.get())}
        return {'Authorization': 'Bearer {0}'.format(self.token.get()),
                'content-type': 'application/json'}

    def send_request(self, method, url, params=None, **url_params):
        params = params or {}
        request_url = f"{self.base_url}{url.format(**url_params)}"
        version = self.login()
        request_params = {
            'headers': self.get_auth_headers(method),
            'verify': self.verify_certificate,
            'timeout': self.configuration.timeout
        }
        if utils.is_version_3(version):
            request_params['auth'] = (self.configuration.username, self.token.get())
            del request_params['headers']['Authorization']

        if method in [self.PUT, self.POST]:
            request_params['data'] = utils.prepare_params(params)
        future = self.session.request(method, request_url, **request_params)
        response = future.result()  # Wait for the request to complete
        self.logout(version)
        return response

    def send_get_request(self, url, params=None, **url_params):
        response = self.send_request(self.GET, url, params, **url_params)
        return response, response.json()

    def send_post_request(self, url, params=None, **url_params):
        response = self.send_request(self.POST, url, params, **url_params)
        return response, response.json()

    def send_put_request(self, url, params=None, **url_params):
        response = self.send_request(self.PUT, url, params, **url_params)
        return response, response.json()

    def send_delete_request(self, url, params=None, **url_params):
        return self.send_request(self.DELETE, url, params, **url_params)

    def send_mdm_cluster_post_request(self, url, params=None, **url_params):
        if params is None:
            params = dict()
        response = None
        version = self.login()
        request_url = self.base_url + url.format(**url_params)
        future = self.session.post(request_url,
                                   auth=(
                                       self.configuration.username,
                                       self.token.get()
                                   ),
                                   headers=self.headers,
                                   data=utils.prepare_params(params),
                                   verify=self.verify_certificate,
                                   timeout=self.configuration.timeout)
        r = future.result()  # Wait for the request to complete

        if r.content != b'':
            response = r.json()
        self.logout(version)
        return r, response

    # To perform login based on the API version
    def login(self):
        version = self.get_api_version()
        if utils.is_version_3(version=version):
            self._login()
        else:
            self._appliance_login()
        return version

    # To perform logout based on the API version
    def logout(self, version):
        if utils.is_version_3(version=version):
            self._logout()
        else:
            self._appliance_logout()

    # Get the Current API version
    def get_api_version(self):
        request_url = self.base_url + '/version'
        self._login()
        future = self.session.get(request_url,
                                  auth=(
                                      self.configuration.username,
                                      self.token.get()),
                                  verify=self.verify_certificate,
                                  timeout=self.configuration.timeout)
        r = future.result()  # Wait for the request to complete
        response = r.json()
        return response

    # API Login method for 4.0 and above.
    def _appliance_login(self):
        request_url = self.auth_url + '/login'
        payload = {"username": "%s" % self.configuration.username,
                   "password": "%s" % self.configuration.password
                   }
        future = self.session.post(request_url, headers=self.headers, json=payload,
                                   verify=self.verify_certificate,
                                   timeout=self.configuration.timeout)
        r = future.result()  # Wait for the request to complete
        if r.status_code != 200:
            exc = exceptions.PowerFlexFailQuerying('token')
            LOG.error(exc.message)
            raise exc
        response = r.json()
        token = response['access_token']
        self.token.set(token)
        self.__refresh_token = response['refresh_token']

    # API logout method for 4.0 and above.
    def _appliance_logout(self):
        request_url = self.auth_url + '/logout'
        data = {'refresh_token': '{0}'.format(self.__refresh_token)}
        future = self.session.post(request_url, headers=self.get_auth_headers(), json=data,
                                   verify=self.verify_certificate,
                                   timeout=self.configuration.timeout)
        r = future.result()  # Wait for the request to complete

        if r.status_code != 204:
            exc = exceptions.PowerFlexFailQuerying('token')
            LOG.error(exc.message)
            raise exc
        self.token.set("")
        self.__refresh_token = None

    def _login(self):
        request_url = self.base_url + '/login'
        try:
            future = self.session.get(request_url,
                                      auth=(
                                          self.configuration.username,
                                          self.configuration.password
                                      ),
                                      verify=self.verify_certificate,
                                      timeout=self.configuration.timeout)
            r = future.result()  # Wait for the request to complete
            r.raise_for_status()
            token = r.json()
            self.token.set(token)
        except Exception as e:
            error_msg = f'Login failed with error:{e.response.content}' if e.response else f'Login failed with error:{str(e)}'
            LOG.error(error_msg)
            raise Exception(error_msg)

    def _logout(self):
        token = self.token.get()

        if token:
            request_url = self.base_url + '/logout'
            future = self.session.get(request_url,
                                      auth=(
                                          self.configuration.username,
                                          token
                                      ),
                                      verify=self.verify_certificate,
                                      timeout=self.configuration.timeout)
            r = future.result()  # Wait for the request to complete
            if r.status_code != 200:
                exc = exceptions.PowerFlexFailQuerying('token')
                LOG.error(exc.message)
                raise exc
            self.token.set("")
```

### Key Notes:
- The `.result()` method ensures that the behavior remains synchronous, as the original code does not use asynchronous patterns.
- The `FuturesSession` object is used consistently across all requests.