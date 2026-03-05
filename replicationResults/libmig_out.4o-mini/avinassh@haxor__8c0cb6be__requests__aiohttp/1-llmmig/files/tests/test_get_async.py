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


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    async def _run_async(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                tasks.append(self.fetch(session, url))
            return await asyncio.gather(*tasks)

    async def fetch(self, session, url):
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

    def test_get_async(self):
        response = asyncio.run(self._run_async([self.url]))
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    def test_get_async_error(self):
        response = asyncio.run(self._run_async([self.err_url]))
        self.assertEqual(response, [None])

    def tearDown(self):
        pass  # No need to close session as it's managed in _run_async

if __name__ == '__main__':
    unittest.main()
