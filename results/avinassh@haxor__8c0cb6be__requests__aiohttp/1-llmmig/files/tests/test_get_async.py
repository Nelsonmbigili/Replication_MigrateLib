#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck
"""

import unittest
import aiohttp
import asyncio

from hackernews import HackerNews


class HackerNews:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def _fetch(self, url):
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except aiohttp.ClientError:
            return None

    async def _run_async(self, urls):
        tasks = [self._fetch(url) for url in urls]
        return await asyncio.gather(*tasks)

    async def close(self):
        await self.session.close()


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_async(self):
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self.hn._run_async([self.url]))
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    def test_get_async_error(self):
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self.hn._run_async([self.err_url]))
        self.assertEqual(response, [None])

    def tearDown(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.hn.close())


if __name__ == '__main__':
    unittest.main()
