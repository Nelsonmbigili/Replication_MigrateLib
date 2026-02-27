#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjke
"""

import unittest
import aiohttp
import asyncio

from hackernews import HackerNews
from hackernews import HTTPError
import pytest


class HackerNews:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def _get_sync(self, url):
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise HTTPError(f"HTTP error: {response.status}")
                return await response.json()
        except aiohttp.ClientResponseError as e:
            raise HTTPError(f"HTTP error: {e.status}") from e
        except Exception as e:
            raise HTTPError("An unexpected error occurred") from e

    async def close(self):
        await self.session.close()


class TestGetSync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    @pytest.mark.asyncio
    async def test_get_sync(self):
        response = await self.hn._get_sync(self.url)
        self.assertEqual(response['id'], 8863)
        self.assertEqual(response['by'], 'dhouston')

    async def test_get_sync_error(self):
        with self.assertRaises(HTTPError):
            await self.hn._get_sync(self.err_url)

    async def asyncTearDown(self):
        await self.hn.close()


if __name__ == '__main__':
    unittest.main()
