from typing import Optional
import urllib3
import json

AUTHOMIZE_API_URL = 'https://api.authomize.com'


class ClientError(Exception):
    def __init__(self, message):
        self.message = message


class BaseClient:
    def __init__(self, auth_token: str, base_url: str = AUTHOMIZE_API_URL):
        self.auth_token = auth_token
        self.base_url = base_url
        self.http = urllib3.PoolManager()
        self.headers = {'Authorization': self.authorization_header}

    @property
    def authorization_header(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _handle_response(response):
        if response.status == 200:
            return BaseClient._handle_ok_response(response)
        try:
            response_json = json.loads(response.data)
            detail = response_json.get('detail')
            if 400 <= response.status < 500:
                response.reason = response.data.decode('utf-8')
        except Exception:
            detail = None
        if detail:
            raise ClientError(str(detail))
        raise ClientError(f"HTTP Error: {response.status}")

    @staticmethod
    def _handle_ok_response(response) -> dict:
        if content_type := response.headers.get('content-type'):
            if content_type.startswith('application/json'):
                return json.loads(response.data)

        raise ClientError(
            message={
                'status_code': response.status,
                'url': response.url,
                'message': 'Unexpected response from API',
                'raw': response.data,
            },
        )

    def http_get(self, url, params=None):
        url = self.base_url + url
        response = self.http.request('GET', url, fields=params, headers=self.headers)
        return self._handle_response(response)

    def http_post(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = self.http.request(
            'POST',
            url,
            headers={'Content-Type': 'application/json', **self.headers},
            body=body,
        )
        return self._handle_response(response)

    def http_patch(self, url: str, body: Optional[str] = None):
        url = self.base_url + url
        response = self.http.request(
            'PATCH',
            url,
            headers={'Content-Type': 'application/json', **self.headers},
            body=body,
        )
        return self._handle_response(response)

    def http_delete(self, url: str, params=None):
        url = self.base_url + url
        response = self.http.request('DELETE', url, fields=params, headers=self.headers)
        return self._handle_response(response)
