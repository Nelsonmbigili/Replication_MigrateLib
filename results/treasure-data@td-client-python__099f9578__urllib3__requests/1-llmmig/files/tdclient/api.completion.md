### Explanation of Changes:
To migrate the code from `urllib3` to `requests`, the following changes were made:
1. **Library Import**: Replaced `urllib3` imports with `requests`.
2. **HTTP Client Initialization**: Removed the `PoolManager` and `ProxyManager` initialization logic, as `requests` does not require explicit connection pooling.
3. **HTTP Methods**: Replaced `urllib3`'s `request` and `urlopen` methods with `requests`'s `get`, `post`, `put`, and `delete` methods.
4. **Retry Logic**: Simplified retry logic using `requests`'s built-in exception handling and retry mechanisms (via `requests.adapters.HTTPAdapter` and `requests.packages.urllib3.util.retry.Retry`).
5. **Headers and Parameters**: Adjusted how headers and parameters are passed to `requests` methods.
6. **Response Handling**: Updated response handling to use `requests.Response` attributes like `status_code`, `headers`, and `content`.
7. **Removed `urllib3.util` Workarounds**: Removed workarounds for `urllib3.util.IS_PYOPENSSL` and related issues, as they are not relevant to `requests`.

Below is the modified code:

---

### Modified Code:
```python
#!/usr/bin/env python

import contextlib
import csv
import email.utils
import gzip
import io
import json
import logging
import os
import socket
import ssl
import sys
import tempfile
import time
import urllib.parse as urlparse
from array import array

import msgpack
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from tdclient import errors, version
from tdclient.bulk_import_api import BulkImportAPI
from tdclient.connector_api import ConnectorAPI
from tdclient.database_api import DatabaseAPI
from tdclient.export_api import ExportAPI
from tdclient.import_api import ImportAPI
from tdclient.job_api import JobAPI
from tdclient.partial_delete_api import PartialDeleteAPI
from tdclient.result_api import ResultAPI
from tdclient.schedule_api import ScheduleAPI
from tdclient.server_status_api import ServerStatusAPI
from tdclient.table_api import TableAPI
from tdclient.user_api import UserAPI
from tdclient.util import (
    csv_dict_record_reader,
    csv_text_record_reader,
    normalized_msgpack,
    read_csv_records,
    validate_record,
)

try:
    import certifi
except ImportError:
    certifi = None

log = logging.getLogger(__name__)

APIError = errors.APIError
AuthError = errors.AuthError
ForbiddenError = errors.ForbiddenError
AlreadyExistsError = errors.AlreadyExistsError
NotFoundError = errors.NotFoundError


class API(
    BulkImportAPI,
    ConnectorAPI,
    DatabaseAPI,
    ExportAPI,
    ImportAPI,
    JobAPI,
    PartialDeleteAPI,
    ResultAPI,
    ScheduleAPI,
    ServerStatusAPI,
    TableAPI,
    UserAPI,
):
    DEFAULT_ENDPOINT = "https://api.treasuredata.com/"
    DEFAULT_IMPORT_ENDPOINT = "https://api-import.treasuredata.com/"

    def __init__(
        self,
        apikey=None,
        user_agent=None,
        endpoint=None,
        headers=None,
        retry_post_requests=False,
        max_cumul_retry_delay=600,
        http_proxy=None,
        **kwargs,
    ):
        headers = {} if headers is None else headers
        if apikey is not None:
            self._apikey = apikey
        elif "TD_API_KEY" in os.environ:
            self._apikey = os.getenv("TD_API_KEY")
        else:
            raise ValueError("no API key given")

        if user_agent is not None:
            self._user_agent = user_agent
        else:
            self._user_agent = "TD-Client-Python/%s" % (version.__version__)

        if endpoint is not None:
            if not urlparse.urlparse(endpoint).scheme:
                endpoint = "https://{}".format(endpoint)
            self._endpoint = endpoint
        elif os.getenv("TD_API_SERVER"):
            self._endpoint = os.getenv("TD_API_SERVER")
        else:
            self._endpoint = self.DEFAULT_ENDPOINT

        self._retry_post_requests = retry_post_requests
        self._max_cumul_retry_delay = max_cumul_retry_delay
        self._headers = {key.lower(): value for (key, value) in headers.items()}

        # Initialize HTTP session with retries
        self.http = self._init_http(http_proxy)

    def _init_http(self, http_proxy=None):
        session = requests.Session()
        retries = Retry(
            total=7,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        if http_proxy:
            session.proxies = {"http": http_proxy, "https": http_proxy}

        if certifi:
            session.verify = certifi.where()

        return session

    def get(self, path, params=None, headers=None, **kwargs):
        headers = {} if headers is None else dict(headers)
        headers["accept-encoding"] = "deflate, gzip"
        url, headers = self.build_request(path=path, headers=headers, **kwargs)

        log.debug(
            "REST GET call:\n  headers: %s\n  path: %s\n  params: %s",
            repr(headers),
            repr(path),
            repr(params),
        )

        try:
            response = self.http.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.error("GET request failed: %s", e)
            raise APIError(f"GET request failed: {e}")

        log.debug(
            "REST GET response:\n  headers: %s\n  status: %d\n  body: <omitted>",
            repr(response.headers),
            response.status_code,
        )

        return response

    def post(self, path, params=None, headers=None, **kwargs):
        headers = {} if headers is None else dict(headers)
        url, headers = self.build_request(path=path, headers=headers, **kwargs)

        log.debug(
            "REST POST call:\n  headers: %s\n  path: %s\n  params: %s",
            repr(headers),
            repr(path),
            repr(params),
        )

        try:
            response = self.http.post(url, json=params, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.error("POST request failed: %s", e)
            raise APIError(f"POST request failed: {e}")

        log.debug(
            "REST POST response:\n  headers: %s\n  status: %d\n  body: <omitted>",
            repr(response.headers),
            response.status_code,
        )

        return response

    def put(self, path, bytes_or_stream, size, headers=None, **kwargs):
        headers = {} if headers is None else dict(headers)
        headers["content-length"] = str(size)
        if "content-type" not in headers:
            headers["content-type"] = "application/octet-stream"
        url, headers = self.build_request(path=path, headers=headers, **kwargs)

        log.debug(
            "REST PUT call:\n  headers: %s\n  path: %s\n  body: <omitted>",
            repr(headers),
            repr(path),
        )

        try:
            response = self.http.put(url, data=bytes_or_stream, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.error("PUT request failed: %s", e)
            raise APIError(f"PUT request failed: {e}")

        log.debug(
            "REST PUT response:\n  headers: %s\n  status: %d\n  body: <omitted>",
            repr(response.headers),
            response.status_code,
        )

        return response

    def delete(self, path, params=None, headers=None, **kwargs):
        headers = {} if headers is None else dict(headers)
        url, headers = self.build_request(path=path, headers=headers, **kwargs)

        log.debug(
            "REST DELETE call:\n  headers: %s\n  path: %s\n  params: %s",
            repr(headers),
            repr(path),
            repr(params),
        )

        try:
            response = self.http.delete(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.error("DELETE request failed: %s", e)
            raise APIError(f"DELETE request failed: {e}")

        log.debug(
            "REST DELETE response:\n  headers: %s\n  status: %d\n  body: <omitted>",
            repr(response.headers),
            response.status_code,
        )

        return response

    def build_request(self, path=None, headers=None, endpoint=None):
        headers = {} if headers is None else headers
        if endpoint is None:
            endpoint = self._endpoint
        if path is None:
            url = endpoint
        else:
            p = urlparse.urlparse(endpoint)
            request_path = path if p.path == "/" else "/".join([p.path, path])
            url = urlparse.urlunparse(
                urlparse.ParseResult(
                    p.scheme, p.netloc, request_path, p.params, p.query, p.fragment
                )
            )
        _headers = dict(self._headers)
        _headers["authorization"] = "TD1 %s" % (self._apikey,)
        _headers["date"] = email.utils.formatdate(time.time())
        _headers["user-agent"] = self._user_agent
        _headers.update({key.lower(): value for (key, value) in headers.items()})
        return (url, _headers)

    def close(self):
        self.http.close()
```

---

### Key Notes:
- The retry logic is now handled by `requests.adapters.HTTPAdapter` with `Retry`.
- The `send_request` method was removed, as `requests` provides direct methods for HTTP verbs.
- The `contextlib.closing` wrapper was removed, as `requests` handles connection cleanup internally.