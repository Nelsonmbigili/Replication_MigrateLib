import unittest
from unittest.mock import MagicMock, call, patch
import arxiv
from datetime import datetime, timedelta
from pytest import approx
import treq
from twisted.web.client import ResponseFailed
from twisted.internet.defer import Deferred
from twisted.web.http_headers import Headers
from twisted.web.iweb import IResponse
from twisted.internet.task import Clock
from twisted.web.test.requesthelper import DummyRequest
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
from twisted.trial.unittest import TestCase
import pytest


def empty_response(code: int) -> IResponse:
    class MockResponse:
        def __init__(self, code):
            self.code = code
            self.headers = Headers({})
            self._body = b""

        def setBody(self, body):
            self._body = body

        def deliverBody(self, protocol):
            protocol.dataReceived(self._body)
            protocol.connectionLost(None)

    return MockResponse(code)


class TestClient(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_invalid_format_id(self):
        with self.assertRaises(arxiv.HTTPError):
            async for _ in await arxiv.Client(num_retries=0).results(arxiv.Search(id_list=["abc"])):
                pass

    @pytest.mark.asyncio
    async def test_invalid_id(self):
        results = [r async for r in await arxiv.Search(id_list=["0000.0000"]).results()]
        self.assertEqual(len(results), 0)

    @pytest.mark.asyncio
    async def test_nonexistent_id_in_list(self):
        client = arxiv.Client()
        # Assert thrown error is handled and hidden by generator.
        results = [r async for r in await client.results(arxiv.Search(id_list=["0808.05394"]))]
        self.assertEqual(len(results), 0)
        # Generator should still yield valid entries.
        results = [r async for r in await client.results(arxiv.Search(id_list=["0808.05394", "1707.08567"]))]
        self.assertEqual(len(results), 1)

    @pytest.mark.asyncio
    async def test_max_results(self):
        client = arxiv.Client(page_size=10)
        search = arxiv.Search(query="testing", max_results=2)
        results = [r async for r in await client.results(search)]
        self.assertEqual(len(results), 2)

    @pytest.mark.asyncio
    async def test_query_page_count(self):
        client = arxiv.Client(page_size=10)
        client._parse_feed = MagicMock(wraps=client._parse_feed)
        generator = await client.results(arxiv.Search(query="testing", max_results=55))
        results = [r async for r in generator]

        # NOTE: don't directly assert on call count; allow for retries.
        unique_urls = set()
        for parse_call in client._parse_feed.call_args_list:
            args, _kwargs = parse_call
            unique_urls.add(args[0])

        self.assertEqual(len(results), 55)
        self.assertSetEqual(
            unique_urls,
            {
                "https://export.arxiv.org/api/query?search_query=testing&id_list=&sortBy=relevance&sortOrder=descending&start=0&max_results=10",
                "https://export.arxiv.org/api/query?search_query=testing&id_list=&sortBy=relevance&sortOrder=descending&start=10&max_results=10",
                "https://export.arxiv.org/api/query?search_query=testing&id_list=&sortBy=relevance&sortOrder=descending&start=20&max_results=10",
                "https://export.arxiv.org/api/query?search_query=testing&id_list=&sortBy=relevance&sortOrder=descending&start=30&max_results=10",
                "https://export.arxiv.org/api/query?search_query=testing&id_list=&sortBy=relevance&sortOrder=descending&start=40&max_results=10",
                "https://export.arxiv.org/api/query?search_query=testing&id_list=&sortBy=relevance&sortOrder=descending&start=50&max_results=10",
            },
        )

    @pytest.mark.asyncio
    async def test_offset(self):
        max_results = 10
        search = arxiv.Search(query="testing", max_results=max_results)
        client = arxiv.Client(page_size=10)

        default = [r async for r in await client.results(search)]
        no_offset = [r async for r in await client.results(search)]
        self.assertListEqual(default, no_offset)

        offset = max_results // 2
        half_offset = [r async for r in await client.results(search, offset=offset)]
        self.assertListEqual(default[offset:], half_offset)

        offset_above_max_results = [r async for r in await client.results(search, offset=max_results)]
        self.assertListEqual(offset_above_max_results, [])

    @pytest.mark.asyncio
    async def test_search_results_offset(self):
        # NOTE: page size is irrelevant here.
        client = arxiv.Client(page_size=15)
        search = arxiv.Search(query="testing", max_results=10)
        all_results = [r async for r in await client.results(search, offset=0)]
        self.assertEqual(len(all_results), 10)

        for offset in [0, 5, 9, 10, 11]:
            client_results = [r async for r in await client.results(search, offset=offset)]
            self.assertEqual(len(client_results), max(0, search.max_results - offset))
            if client_results:
                self.assertEqual(all_results[offset].entry_id, client_results[0].entry_id)

    @pytest.mark.asyncio
    async def test_no_duplicates(self):
        search = arxiv.Search("testing", max_results=100)
        ids = set()
        async for r in await search.results():
            self.assertFalse(r.entry_id in ids)
            ids.add(r.entry_id)

    @pytest.mark.asyncio
    @patch("treq.get", return_value=empty_response(500))
    @patch("time.sleep", return_value=None)
    async def test_retry(self, mock_sleep, mock_get):
        broken_client = arxiv.Client()

        async def broken_get():
            search = arxiv.Search(query="quantum")
            return await anext(await broken_client.results(search))

        with self.assertRaises(arxiv.HTTPError):
            await broken_get()

        for num_retries in [2, 5]:
            broken_client.num_retries = num_retries
            try:
                await broken_get()
                self.fail("broken_get didn't throw HTTPError")
            except arxiv.HTTPError as e:
                self.assertEqual(e.status, 500)
                self.assertEqual(e.retry, broken_client.num_retries)

    @pytest.mark.asyncio
    @patch("treq.get", return_value=empty_response(200))
    @patch("time.sleep", return_value=None)
    async def test_sleep_standard(self, mock_sleep, mock_get):
        client = arxiv.Client()
        url = client._format_url(arxiv.Search(query="quantum"), 0, 1)
        # A client should sleep until delay_seconds have passed.
        await client._parse_feed(url)
        mock_sleep.assert_not_called()
        # Overwrite _last_request_dt to minimize flakiness: different
        # environments will have different page fetch times.
        client._last_request_dt = datetime.now()
        await client._parse_feed(url)
        mock_sleep.assert_called_once_with(approx(client.delay_seconds, rel=1e-3))

    @pytest.mark.asyncio
    @patch("treq.get", return_value=empty_response(200))
    @patch("time.sleep", return_value=None)
    async def test_sleep_multiple_requests(self, mock_sleep, mock_get):
        client = arxiv.Client()
        url1 = client._format_url(arxiv.Search(query="quantum"), 0, 1)
        url2 = client._format_url(arxiv.Search(query="testing"), 0, 1)
        # Rate limiting is URL-independent; expect same behavior as in
        # `test_sleep_standard`.
        await client._parse_feed(url1)
        mock_sleep.assert_not_called()
        client._last_request_dt = datetime.now()
        await client._parse_feed(url2)
        mock_sleep.assert_called_once_with(approx(client.delay_seconds, rel=1e-3))

    @pytest.mark.asyncio
    @patch("treq.get", return_value=empty_response(200))
    @patch("time.sleep", return_value=None)
    async def test_sleep_elapsed(self, mock_sleep, mock_get):
        client = arxiv.Client()
        url = client._format_url(arxiv.Search(query="quantum"), 0, 1)
        # If _last_request_dt is less than delay_seconds ago, sleep.
        client._last_request_dt = datetime.now() - timedelta(seconds=client.delay_seconds - 1)
        await client._parse_feed(url)
        mock_sleep.assert_called_once()
        mock_sleep.reset_mock()
        # If _last_request_dt is at least delay_seconds ago, don't sleep.
        client._last_request_dt = datetime.now() - timedelta(seconds=client.delay_seconds)
        await client._parse_feed(url)
        mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    @patch("treq.get", return_value=empty_response(200))
    @patch("time.sleep", return_value=None)
    async def test_sleep_zero_delay(self, mock_sleep, mock_get):
        client = arxiv.Client(delay_seconds=0)
        url = client._format_url(arxiv.Search(query="quantum"), 0, 1)
        await client._parse_feed(url)
        await client._parse_feed(url)
        mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    @patch("treq.get", return_value=empty_response(500))
    @patch("time.sleep", return_value=None)
    async def test_sleep_between_errors(self, mock_sleep, mock_get):
        client = arxiv.Client()
        url = client._format_url(arxiv.Search(query="quantum"), 0, 1)
        try:
            await client._parse_feed(url)
        except arxiv.HTTPError:
            pass
        # Should sleep between retries.
        mock_sleep.assert_called()
        self.assertEqual(mock_sleep.call_count, client.num_retries)
        mock_sleep.assert_has_calls(
            [
                call(approx(client.delay_seconds, abs=1e-2)),
            ]
            * client.num_retries
        )
