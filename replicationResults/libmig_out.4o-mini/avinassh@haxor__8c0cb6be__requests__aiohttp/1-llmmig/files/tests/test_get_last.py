#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import aiohttp
import asyncio

from hackernews import HackerNews
from hackernews import Item


class TestGetLast(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    async def async_setUp(self):
        self.hn.session = aiohttp.ClientSession()

    async def async_tearDown(self):
        await self.hn.session.close()

    def test_get_item(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_setUp())
        items = loop.run_until_complete(self.hn.get_last(5))
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 5)
        self.assertIsInstance(items[0], Item)
        loop.run_until_complete(self.async_tearDown())

if __name__ == '__main__':
    unittest.main()
