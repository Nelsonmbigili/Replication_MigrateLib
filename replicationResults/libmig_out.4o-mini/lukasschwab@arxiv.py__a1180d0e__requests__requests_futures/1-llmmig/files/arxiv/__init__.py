""".. include:: ../README.md"""
from __future__ import annotations

import logging
import time
import itertools
import feedparser
import os
import math
import re
import warnings
from requests_futures.sessions import FuturesSession  # Changed import
from urllib.parse import urlencode
from urllib.request import urlretrieve
from datetime import datetime, timedelta, timezone
from calendar import timegm

from enum import Enum
from typing import Dict, Generator, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_TIME = datetime.min


class Result(object):
    # ... [rest of the Result class remains unchanged] ...

class SortCriterion(Enum):
    # ... [rest of the SortCriterion class remains unchanged] ...

class SortOrder(Enum):
    # ... [rest of the SortOrder class remains unchanged] ...

class Search(object):
    # ... [rest of the Search class remains unchanged] ...

class Client(object):
    """
    Specifies a strategy for fetching results from arXiv's API.

    This class obscures pagination and retry logic, and exposes
    `Client.results`.
    """

    query_url_format = "https://export.arxiv.org/api/query?{}"
    page_size: int
    delay_seconds: float
    num_retries: int

    _last_request_dt: datetime
    _session: FuturesSession  # Changed to FuturesSession

    def __init__(self, page_size: int = 100, delay_seconds: float = 3.0, num_retries: int = 3):
        self.page_size = page_size
        self.delay_seconds = delay_seconds
        self.num_retries = num_retries
        self._last_request_dt = None
        self._session = FuturesSession()  # Changed to FuturesSession

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return "{}(page_size={}, delay_seconds={}, num_retries={})".format(
            _classname(self),
            repr(self.page_size),
            repr(self.delay_seconds),
            repr(self.num_retries),
        )

    def results(self, search: Search, offset: int = 0) -> Generator[Result, None, None]:
        limit = search.max_results - offset if search.max_results else None
        if limit and limit < 0:
            return iter(())
        return itertools.islice(self._results(search, offset), limit)

    def _results(self, search: Search, offset: int = 0) -> Generator[Result, None, None]:
        page_url = self._format_url(search, offset, self.page_size)
        feed = self._parse_feed(page_url, first_page=True)
        if not feed.entries:
            logger.info("Got empty first page; stopping generation")
            return
        total_results = int(feed.feed.opensearch_totalresults)
        logger.info(
            "Got first page: %d of %d total results",
            len(feed.entries),
            total_results,
        )

        while feed.entries:
            for entry in feed.entries:
                try:
                    yield Result._from_feed_entry(entry)
                except Result.MissingFieldError as e:
                    logger.warning("Skipping partial result: %s", e)
            offset += len(feed.entries)
            if offset >= total_results:
                break
            page_url = self._format_url(search, offset, self.page_size)
            feed = self._parse_feed(page_url, first_page=False)

    def _format_url(self, search: Search, start: int, page_size: int) -> str:
        url_args = search._url_args()
        url_args.update(
            {
                "start": start,
                "max_results": page_size,
            }
        )
        return self.query_url_format.format(urlencode(url_args))

    def _parse_feed(
        self, url: str, first_page: bool = True, _try_index: int = 0
    ) -> feedparser.FeedParserDict:
        try:
            return self.__try_parse_feed(url, first_page=first_page, try_index=_try_index)
        except (
            HTTPError,
            UnexpectedEmptyPageError,
            requests.exceptions.ConnectionError,
        ) as err:
            if _try_index < self.num_retries:
                logger.debug("Got error (try %d): %s", _try_index, err)
                return self._parse_feed(url, first_page=first_page, _try_index=_try_index + 1)
            logger.debug("Giving up (try %d): %s", _try_index, err)
            raise err

    def __try_parse_feed(
        self,
        url: str,
        first_page: bool,
        try_index: int,
    ) -> feedparser.FeedParserDict:
        if self._last_request_dt is not None:
            required = timedelta(seconds=self.delay_seconds)
            since_last_request = datetime.now() - self._last_request_dt
            if since_last_request < required:
                to_sleep = (required - since_last_request).total_seconds()
                logger.info("Sleeping: %f seconds", to_sleep)
                time.sleep(to_sleep)

        logger.info("Requesting page (first: %r, try: %d): %s", first_page, try_index, url)

        future = self._session.get(url, headers={"user-agent": "arxiv.py/2.1.3"})  # Changed to use FuturesSession
        self._last_request_dt = datetime.now()
        resp = future.result()  # Get the response from the Future
        if resp.status_code != requests.codes.OK:
            raise HTTPError(url, try_index, resp.status_code)

        feed = feedparser.parse(resp.content)
        if len(feed.entries) == 0 and not first_page:
            raise UnexpectedEmptyPageError(url, try_index, feed)

        if feed.bozo:
            logger.warning(
                "Bozo feed; consider handling: %s",
                feed.bozo_exception if "bozo_exception" in feed else None,
            )

        return feed

# ... [rest of the classes remain unchanged] ...
