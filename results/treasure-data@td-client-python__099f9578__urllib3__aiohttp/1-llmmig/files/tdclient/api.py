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
import aiohttp

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

        # Initialize aiohttp session
        self.session = aiohttp.ClientSession()

    @property
    def apikey(self):
        return self._apikey

    @property
    def endpoint(self):
        return self._endpoint

    async def get(self, path, params=None, headers=None, **kwargs):
        headers = {} if headers is None else dict(headers)
        headers["accept-encoding"] = "deflate, gzip"
        url, headers = self.build_request(path=path, headers=headers, **kwargs)

        log.debug(
            "REST GET call:\n  headers: %s\n  path: %s\n  params: %s",
            repr(headers),
            repr(path),
            repr(params),
        )

        retry_delay = 5
        cumul_retry_delay = 0

        while True:
            try:
                async with self.session.get(url, params=params, headers=headers) as response:
                    if response.status < 500:
                        log.debug(
                            "REST GET response:\n  headers: %s\n  status: %d\n  body: <omitted>",
                            repr(dict(response.headers)),
                            response.status,
                        )
                        return response
                    else:
                        log.warning(
                            "Error %d: %s. Retrying after %d seconds... (cumulative: %d/%d)",
                            response.status,
                            await response.text(),
                            retry_delay,
                            cumul_retry_delay,
                            self._max_cumul_retry_delay,
                        )
            except aiohttp.ClientError as e:
                log.warning("Client error: %s. Retrying...", str(e))

            if cumul_retry_delay <= self._max_cumul_retry_delay:
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

    async def post(self, path, params=None, headers=None, **kwargs):
        headers = {} if headers is None else dict(headers)
        url, headers = self.build_request(path=path, headers=headers, **kwargs)

        log.debug(
            "REST POST call:\n  headers: %s\n  path: %s\n  params: %s",
            repr(headers),
            repr(path),
            repr(params),
        )

        retry_delay = 5
        cumul_retry_delay = 0

        while True:
            try:
                async with self.session.post(url, json=params, headers=headers) as response:
                    if response.status < 500:
                        log.debug(
                            "REST POST response:\n  headers: %s\n  status: %d\n  body: <omitted>",
                            repr(dict(response.headers)),
                            response.status,
                        )
                        return response
                    else:
                        log.warning(
                            "Error %d: %s. Retrying after %d seconds... (cumulative: %d/%d)",
                            response.status,
                            await response.text(),
                            retry_delay,
                            cumul_retry_delay,
                            self._max_cumul_retry_delay,
                        )
            except aiohttp.ClientError as e:
                log.warning("Client error: %s. Retrying...", str(e))

            if cumul_retry_delay <= self._max_cumul_retry_delay:
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

    async def close(self):
        await self.session.close()
