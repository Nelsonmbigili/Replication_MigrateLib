""".. include:: ../README.md"""
from __future__ import annotations

import logging
import time
import itertools
import feedparser
import os
import math
import re
import aiohttp
import asyncio
import warnings

from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
from calendar import timegm

from enum import Enum
from typing import Dict, Generator, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_TIME = datetime.min


class Result(object):
    # ... (unchanged code)

    def download_pdf(self, dirpath: str = "./", filename: str = "") -> str:
        # ... (unchanged code)

    def download_source(self, dirpath: str = "./", filename: str = "") -> str:
        # ... (unchanged code)

    # ... (unchanged code)


class SortCriterion(Enum):
    # ... (unchanged code)


class SortOrder(Enum):
    # ... (unchanged code)


class Search(object):
    # ... (unchanged code)

    async def results(self, offset: int = 0) -> Generator[Result, None, None]:
        """
        Executes the specified search using a default arXiv API client. For info
        on default behavior, see `Client.__init__` and `Client.results`.

        **Deprecated** after 2.0.0; use `Client.results` instead.
        """
        warnings.warn(
            "The 'Search.results' method is deprecated, use 'Client.results' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return await Client().results(self, offset=offset)


class Client(object):
    query_url_format = "https://export.arxiv.org/api/query?{}"
    # ... (unchanged code)

    def __init__(self, page_size: int = 100, delay_seconds: float = 3.0, num_retries: int = 3):
        # ... (unchanged code)
        self._session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()

    async def results(self, search: Search, offset: int = 0) -> Generator[Result, None, None]:
        limit = search.max_results - offset if search.max_results else None
        if limit and limit < 0:
            return iter(())
        return itertools.islice(await self._results(search, offset), limit)

    async def _results(self, search: Search, offset: int = 0) -> Generator[Result, None, None]:
        page_url = self._format_url(search, offset, self.page_size)
        feed = await self._parse_feed(page_url, first_page=True)
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
            feed = await self._parse_feed(page_url, first_page=False)

    async def _parse_feed(
        self, url: str, first_page: bool = True, _try_index: int = 0
    ) -> feedparser.FeedParserDict:
        try:
            return await self.__try_parse_feed(url, first_page=first_page, try_index=_try_index)
        except (
            HTTPError,
            UnexpectedEmptyPageError,
            aiohttp.ClientConnectionError,
        ) as err:
            if _try_index < self.num_retries:
                logger.debug("Got error (try %d): %s", _try_index, err)
                return await self._parse_feed(url, first_page=first_page, _try_index=_try_index + 1)
            logger.debug("Giving up (try %d): %s", _try_index, err)
            raise err

    async def __try_parse_feed(
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
                await asyncio.sleep(to_sleep)

        logger.info("Requesting page (first: %r, try: %d): %s", first_page, try_index, url)

        async with self._session.get(url, headers={"user-agent": "arxiv.py/2.1.3"}) as resp:
            self._last_request_dt = datetime.now()
            if resp.status != 200:
                raise HTTPError(url, try_index, resp.status)

            feed = feedparser.parse(await resp.text())
            if len(feed.entries) == 0 and not first_page:
                raise UnexpectedEmptyPageError(url, try_index, feed)

            if feed.bozo:
                logger.warning(
                    "Bozo feed; consider handling: %s",
                    feed.bozo_exception if "bozo_exception" in feed else None,
                )

            return feed


class ArxivError(Exception):
    # ... (unchanged code)


class UnexpectedEmptyPageError(ArxivError):
    # ... (unchanged code)


class HTTPError(ArxivError):
    # ... (unchanged code)


def _classname(o):
    """A helper function for use in __repr__ methods: arxiv.Result.Link."""
    return "arxiv.{}".format(o.__class__.__qualname__)
