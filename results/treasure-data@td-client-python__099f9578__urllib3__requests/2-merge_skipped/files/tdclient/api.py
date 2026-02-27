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
    """Internal API class

    Args:
        apikey (str): the API key of Treasure Data Service. If `None` is given, `TD_API_KEY` will be used if available.
        user_agent (str): custom User-Agent.
        endpoint (str): custom endpoint URL. If `None` is given, `TD_API_SERVER` will be used if available.
        headers (dict): custom HTTP headers.
        retry_post_requests (bool): Specify whether allowing API client to retry POST requests. `False` by default.
        max_cumul_retry_delay (int): maximum retry limit in seconds. 600 seconds by default.
        http_proxy (str): HTTP proxy setting. if `None` is given, `HTTP_PROXY` will be used if available.
    """

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

        pool_options = dict(kwargs)
        if "ca_certs" not in pool_options and certifi:
            pool_options["ca_certs"] = certifi.where()

        if pool_options.get("ca_certs") is not None:
            pool_options["cert_reqs"] = ssl.CERT_REQUIRED

        if "timeout" not in pool_options:
            pool_options["timeout"] = 60

        self.http = self._init_http(
            http_proxy if http_proxy else os.getenv("HTTP_PROXY"), **pool_options
        )
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
        # up to 7 retries with exponential (base 2) back-off starting at 'retry_delay'
        retry_delay = 5
        cumul_retry_delay = 0

        # for both exceptions and 500+ errors retrying is enabled by default.
        # The total number of retries cumulatively should not exceed 10 minutes / 600 seconds
        response = None
        while True:
            try:
                response = self.send_request(
                    "GET",
                    url,
                    fields=params,
                    headers=headers,
                    decode_content=True,
                    preload_content=False,
                )
                # retry if the HTTP error code is 500 or higher and we did not run out of retrying attempts
                if response.status < 500:
                    break
                else:
                    log.warning(
                        "Error %d: %s. Retrying after %d seconds... (cumulative: %d/%d)",
                        response.status,
                        response.data,
                        retry_delay,
                        cumul_retry_delay,
                        self._max_cumul_retry_delay,
                    )
            except (
                urllib3.exceptions.TimeoutStateError,
                urllib3.exceptions.TimeoutError,
                urllib3.exceptions.PoolError,
                http.client.IncompleteRead,
                TimeoutError,
                socket.error,
            ):
                pass

            if cumul_retry_delay <= self._max_cumul_retry_delay:
                log.warning(
                    "Retrying after %d seconds... (cumulative: %d/%d)",
                    retry_delay,
                    cumul_retry_delay,
                    self._max_cumul_retry_delay,
                )
                time.sleep(retry_delay)
                cumul_retry_delay += retry_delay
                retry_delay *= 2
            else:
                raise APIError(
                    "Retrying stopped after %d seconds. (cumulative: %d/%d)"
                    % (
                        self._max_cumul_retry_delay,
                        cumul_retry_delay,
                        self._max_cumul_retry_delay,
                    )
                )
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
        # up to 7 retries with exponential (base 2) back-off starting at 'retry_delay'
        retry_delay = 5
        cumul_retry_delay = 0

        # for both exceptions and 500+ errors retrying can be enabled by initialization
        # parameter 'retry_post_requests'. The total number of retries cumulatively
        # should not exceed 10 minutes / 600 seconds

        # use `params` as request parameter if it is a `dict`.
        # otherwise, use it as byte string of request body.
        body = fields = None
        if isinstance(params, dict):
            fields = params
        else:
            body = params

        response = None
        while True:
            try:
                response = self.send_request(
                    "POST",
                    url,
                    fields=fields,
                    body=body,
                    headers=headers,
                    decode_content=True,
                    preload_content=False,
                )
                # if the HTTP error code is 500 or higher and the user requested retrying
                # on post request, attempt a retry
                if response.status < 500:
                    break
                else:
                    if not self._retry_post_requests:
                        raise APIError(
                            "Retrying stopped by retry_post_requests == False"
                        )
                    log.warning(
                        "Error %d: %s. Retrying after %d seconds... (cumulative: %d/%d)",
                        response.status,
                        response.data,
                        retry_delay,
                        cumul_retry_delay,
                        self._max_cumul_retry_delay,
                    )
            except (
                urllib3.exceptions.TimeoutStateError,
                urllib3.exceptions.TimeoutError,
                urllib3.exceptions.PoolError,
                socket.error,
            ):
                if not self._retry_post_requests:
                    raise APIError("Retrying stopped by retry_post_requests == False")

            if cumul_retry_delay <= self._max_cumul_retry_delay:
                log.warning(
                    "Retrying after %d seconds... (cumulative: %d/%d)",
                    retry_delay,
                    cumul_retry_delay,
                    self._max_cumul_retry_delay,
                )
                time.sleep(retry_delay)
                cumul_retry_delay += retry_delay
                retry_delay *= 2
            else:
                raise APIError(
                    "Retrying stopped after %d seconds. (cumulative: %d/%d)"
                    % (
                        self._max_cumul_retry_delay,
                        cumul_retry_delay,
                        self._max_cumul_retry_delay,
                    )
                )
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
        # up to 7 retries with exponential (base 2) back-off starting at 'retry_delay'
        retry_delay = 5
        cumul_retry_delay = 0

        # for both exceptions and 500+ errors retrying is enabled by default.
        # The total number of retries cumulatively should not exceed 10 minutes / 600 seconds
        response = None
        while True:
            try:
                response = self.send_request(
                    "DELETE",
                    url,
                    fields=params,
                    headers=headers,
                    decode_content=True,
                    preload_content=False,
                )
                # retry if the HTTP error code is 500 or higher and we did not run out of retrying attempts
                if response.status < 500:
                    break
                else:
                    log.warning(
                        "Error %d: %s. Retrying after %d seconds... (cumulative: %d/%d)",
                        response.status,
                        response.data,
                        retry_delay,
                        cumul_retry_delay,
                        self._max_cumul_retry_delay,
                    )
            except (
                urllib3.exceptions.TimeoutStateError,
                urllib3.exceptions.TimeoutError,
                urllib3.exceptions.PoolError,
                socket.error,
            ):
                pass

            if cumul_retry_delay <= self._max_cumul_retry_delay:
                log.warning(
                    "Retrying after %d seconds... (cumulative: %d/%d)",
                    retry_delay,
                    cumul_retry_delay,
                    self._max_cumul_retry_delay,
                )
                time.sleep(retry_delay)
                cumul_retry_delay += retry_delay
                retry_delay *= 2
            else:
                raise APIError(
                    "Retrying stopped after %d seconds. (cumulative: %d/%d)"
                    % (
                        self._max_cumul_retry_delay,
                        cumul_retry_delay,
                        self._max_cumul_retry_delay,
                    )
                )
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

    def send_request(self, method, url, fields=None, body=None, headers=None, **kwargs):
        if body is None:
            return self.http.request(
                method, url, fields=fields, headers=headers, **kwargs
            )

        if urllib3.util.IS_PYOPENSSL and isinstance(body, bytearray):
            # workaround for https://github.com/pyca/pyopenssl/issues/621
            body = memoryview(body)
        if urllib3.util.IS_PYOPENSSL and isinstance(body, array):
            # workaround for https://github.com/pyca/pyopenssl/issues/621
            body = body.tobytes()
        return self.http.urlopen(method, url, body=body, headers=headers, **kwargs)

    def raise_error(self, msg, res, body):
        status_code = res.status
        s = body if isinstance(body, str) else body.decode("utf-8")
        if status_code == 404:
            raise errors.NotFoundError("%s: %s" % (msg, s))
        elif status_code == 409:
            raise errors.AlreadyExistsError("%s: %s" % (msg, s))
        elif status_code == 401:
            raise errors.AuthError("%s: %s" % (msg, s))
        elif status_code == 403:
            raise errors.ForbiddenError("%s: %s" % (msg, s))
        else:
            raise errors.APIError("%d: %s: %s" % (status_code, msg, s))

    def checked_json(self, body, required):
        js = None
        try:
            js = json.loads(body.decode("utf-8"))
        except ValueError as error:
            raise APIError("Unexpected API response: %s: %s" % (error, repr(body)))
        js = dict(js)
        if 0 < [k in js for k in required].count(False):
            missing = [k for k in required if k not in js]
            raise APIError(
                "Unexpected API response: %s: %s" % (repr(missing), repr(body))
            )
        return js

    def close(self):
        self.http.close()
        # urllib3 doesn't allow to close all connections immediately.
        # all connections in pool will be closed eventually during gc.
        self.http.clear()

    def _prepare_file(self, file_like, fmt, **kwargs):
        fp = tempfile.TemporaryFile()
        with contextlib.closing(gzip.GzipFile(mode="wb", fileobj=fp)) as gz:
            packer = msgpack.Packer()
            with contextlib.closing(self._read_file(file_like, fmt, **kwargs)) as items:
                for item in items:
                    try:
                        mp = packer.pack(item)
                    except (OverflowError, ValueError):
                        packer.reset()
                        mp = packer.pack(normalized_msgpack(item))
                    gz.write(mp)
        fp.seek(0)
        return fp

    def _read_file(self, file_like, fmt, **kwargs):
        compressed = fmt.endswith(".gz")
        if compressed:
            fmt = fmt[0 : len(fmt) - len(".gz")]
        reader_name = "_read_%s_file" % (fmt,)
        if hasattr(self, reader_name):
            reader = getattr(self, reader_name)
        else:
            raise TypeError("unknown format: %s" % (fmt,))
        if hasattr(file_like, "read"):
            if compressed:
                file_like = gzip.GzipFile(fileobj=file_like)
            return reader(file_like, **kwargs)
        else:
            if compressed:
                file_like = gzip.GzipFile(fileobj=open(file_like, "rb"))
            else:
                file_like = open(file_like, "rb")
            return reader(file_like, **kwargs)

    def _read_msgpack_file(self, file_like, **kwargs):
        # current impl doesn't tolerate any unpack error
        unpacker = msgpack.Unpacker(file_like, raw=False)
        for record in unpacker:
            validate_record(record)
            yield record

    def _read_json_file(self, file_like, **kwargs):
        # current impl doesn't tolerate any JSON parse error
        for s in file_like:
            record = json.loads(s.decode("utf-8"))
            validate_record(record)
            yield record

    def _read_csv_file(
        self,
        file_like,
        dialect=csv.excel,
        columns=None,
        encoding="utf-8",
        dtypes=None,
        converters=None,
        **kwargs,
    ):
        if columns is None:
            reader = csv_dict_record_reader(file_like, encoding, dialect)
        else:
            reader = csv_text_record_reader(file_like, encoding, dialect, columns)

        return read_csv_records(reader, dtypes, converters, **kwargs)

    def _read_tsv_file(self, file_like, **kwargs):
        return self._read_csv_file(file_like, dialect=csv.excel_tab, **kwargs)