#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjke
"""

import unittest
import asyncio
import treq

from hackernews import HackerNews
import pytest


class HackerNews:
    async def _run_async(self, urls):
        results = []
        for url in urls:
            try:
                response = await treq.get(url)
                if response.code == 200:
                    json_data = await treq.json_content(response)
                    results.append(json_data)
                else:
                    results.append(None)
            except Exception:
                results.append(None)
        return results


class TestGetAsync(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    @pytest.mark.asyncio
    async def test_get_async(self):
        response = await self.hn._run_async([self.url])
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    @pytest.mark.asyncio
    async def test_get_async_error(self):
        response = await self.hn._run_async([self.err_url])
        self.assertEqual(response, [None])

if __name__ == '__main__':
    unittest.main()
