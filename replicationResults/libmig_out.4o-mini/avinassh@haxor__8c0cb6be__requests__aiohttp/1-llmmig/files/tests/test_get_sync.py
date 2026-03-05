#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import aiohttp
import asyncio

from hackernews import HackerNews
from hackernews import HTTPError


class TestGetSync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    async def _get_async(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    def test_get_sync(self):
        response = asyncio.run(self._get_async(self.url))
        self.assertEqual(response['id'], 8863)
        self.assertEqual(response['by'], 'dhouston')

    def test_get_sync_error(self):
        with self.assertRaises(HTTPError):
            asyncio.run(self._get_async(self.err_url))

    def tearDown(self):
        pass  # No need to close session as it's handled in _get_async

if __name__ == '__main__':
    unittest.main()
