import urllib3
import json
from .enums import Requests
from .constants import Constants

class ApiService(Constants):
    def __init__(self):
        Constants.__init__(self)
        self.manager = urllib3.PoolManager()  # Create a PoolManager instance for HTTP requests

    def api_call_helper(self, name, http_method, params, data):
        """helper formats the url and reads error codes nicely"""
        config = self._service_config
        url = f"{config['host']}{config['routes'][name][0]}"
        if params is not None:
            url = url.format(**params)
        jwt_token = self.validate_token(config, name)
        response = self._api_call(url, http_method, jwt_token, data)
        if response.status != 200:  # urllib3 uses `status` instead of `status_code`
            if response.status == 400:
                raise AttributeError(response.data.decode('utf-8'))
            elif response.status == 404:
                raise Exception(response.data.decode('utf-8'))
            elif response.status == 415:
                raise Exception(response.data.decode('utf-8'))
            elif response.status == 500:
                raise Exception(response.data.decode('utf-8'))
            elif response.status == 401:
                raise ConnectionError(response.data.decode('utf-8'))
            else:
                raise Exception(response.data.decode('utf-8'))  # Generic exception for other status codes
        if not url.find('security_master') == -1:
            return response.data.decode('utf-8')  # Decode response data to string
        else:
            return json.loads(response.data.decode('utf-8'))  # Decode and parse JSON response

    def _api_call(self, url, http_method, jwt_token, data):
        """Checks for the API Method and that call is done and returned"""
        headers = {'Content-Type': "application/json",
                   'openapi-client-src': "sdk"}
        if jwt_token is not None:
            headers['x-jwt-token'] = jwt_token
        r = None
        if http_method is Requests.POST:
            r = self.manager.request(
                "POST", url, body=json.dumps(data).encode('utf-8'), headers=headers
            )
        elif http_method is Requests.DELETE:
            r = self.manager.request("DELETE", url, headers=headers)
        elif http_method is Requests.PUT:
            r = self.manager.request(
                "PUT", url, body=json.dumps(data).encode('utf-8'), headers=headers
            )
        elif http_method is Requests.GET:
            r = self.manager.request("GET", url, headers=headers)
        return r

    def validate_token(self, config, name):
        """
        Validate jwt tokens 
        """
        tokens = (config['routes'][name][1])
        jwt_token = None
        if self.access_token is not None and "access_token" in tokens:
            jwt_token = self.access_token
        if self.public_access_token is not None and "public_access_token" in tokens:
            jwt_token = self.public_access_token
        if self.read_access_token is not None and "read_access_token" in tokens:
            jwt_token = self.read_access_token
        if len(tokens) > 0 and jwt_token is None:
            raise TypeError("Token is invalid: " + ' or '.join(tokens))
        else:
            return jwt_token
